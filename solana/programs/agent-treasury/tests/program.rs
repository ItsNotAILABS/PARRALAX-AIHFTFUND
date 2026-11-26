//! Program tests for the agent treasury (review finding H4).
//!
//! Runs against the compiled SBF program when `SBF_OUT_DIR` points at the
//! directory containing `parralax_agent_treasury.so` (CI does this after
//! `anchor build`), and against the native build otherwise. Every negative case
//! asserts the exact error code, not just "some error".
use anchor_lang::{AccountDeserialize, InstructionData, ToAccountMetas};
use parralax_agent_treasury::{self as prog, PolicyParams, Treasury, TREASURY_SEED};
use solana_program_test::{processor, BanksClientError, ProgramTest, ProgramTestContext};
use solana_sdk::{
    account_info::AccountInfo,
    clock::Clock,
    entrypoint::ProgramResult,
    instruction::{Instruction, InstructionError},
    program_pack::Pack,
    pubkey::Pubkey,
    signature::Keypair,
    signer::Signer,
    system_instruction, system_program,
    transaction::{Transaction, TransactionError},
};
use spl_associated_token_account::get_associated_token_address;

const DAY: i64 = 86_400;
const PER_TX: u64 = 1_000_000;
const DAILY: u64 = 2_000_000;
const LIFETIME: u64 = 4_000_000;

// Anchor custom errors (6000 + index) and framework constraint errors.
const INVALID_AUTHORITY: u32 = 6000;
const INVALID_CAPS: u32 = 6001;
const EXPIRED: u32 = 6002;
const REVOKED: u32 = 6003;
const INVALID_AMOUNT: u32 = 6004;
const PER_TX_LIMIT: u32 = 6005;
const DAILY_LIMIT: u32 = 6006;
const LIFETIME_LIMIT: u32 = 6007;
const INVALID_NONCE: u32 = 6008;
const PAUSED: u32 = 6010;
const UNAUTHORIZED: u32 = 6011;
const MINT_NOT_ALLOWED: u32 = 6012;
const INVALID_EXPIRY: u32 = 6013;
const CONSTRAINT_HAS_ONE: u32 = 2001;
const CONSTRAINT_ASSOCIATED: u32 = 2009;
const CONSTRAINT_TOKEN_OWNER: u32 = 2015;
const ACCOUNT_NOT_INITIALIZED: u32 = 3012;

fn native_entry(program_id: &Pubkey, accounts: &[AccountInfo], data: &[u8]) -> ProgramResult {
    // Anchor's entry wants `&'info [AccountInfo<'info>]`; program-test's native
    // processor type has independent lifetimes. Safe for the call's duration.
    let accounts: &[AccountInfo] = unsafe { std::mem::transmute(accounts) };
    prog::entry(program_id, accounts, data)
}

fn program_test() -> ProgramTest {
    if std::env::var_os("SBF_OUT_DIR").is_some() || std::env::var_os("BPF_OUT_DIR").is_some() {
        let mut pt = ProgramTest::new("parralax_agent_treasury", prog::ID, None);
        pt.prefer_bpf(true);
        pt
    } else {
        ProgramTest::new(
            "parralax_agent_treasury",
            prog::ID,
            processor!(native_entry),
        )
    }
}

fn treasury_pda(owner: &Pubkey, mint: &Pubkey, seed_id: u64) -> Pubkey {
    Pubkey::find_program_address(
        &[
            TREASURY_SEED,
            owner.as_ref(),
            mint.as_ref(),
            &seed_id.to_le_bytes(),
        ],
        &prog::ID,
    )
    .0
}

fn ix(accounts: impl ToAccountMetas, data: impl InstructionData) -> Instruction {
    Instruction {
        program_id: prog::ID,
        accounts: accounts.to_account_metas(None),
        data: data.data(),
    }
}

#[track_caller]
fn assert_code(res: Result<(), BanksClientError>, code: u32) {
    match res {
        Ok(()) => panic!("expected error {code}, transaction succeeded"),
        Err(e) => match e.unwrap() {
            TransactionError::InstructionError(_, InstructionError::Custom(c)) => {
                assert_eq!(c, code, "wrong error code")
            }
            other => panic!("expected custom error {code}, got {other:?}"),
        },
    }
}

struct Env {
    ctx: ProgramTestContext,
    owner: Keypair,
    agent: Keypair,
    beneficiary: Keypair,
    guardian: Keypair,
    mint: Pubkey,
    seed_id: u64,
    treasury: Pubkey,
    vault: Pubkey,
    owner_token: Pubkey,
    beneficiary_token: Pubkey,
}

impl Env {
    async fn new() -> Self {
        let ctx = program_test().start_with_context().await;
        let owner = ctx.payer.insecure_clone();
        let mut env = Env {
            ctx,
            owner,
            agent: Keypair::new(),
            beneficiary: Keypair::new(),
            guardian: Keypair::new(),
            mint: Pubkey::default(),
            seed_id: 7,
            treasury: Pubkey::default(),
            vault: Pubkey::default(),
            owner_token: Pubkey::default(),
            beneficiary_token: Pubkey::default(),
        };
        env.mint = env.create_mint(None).await;
        env.treasury = treasury_pda(&env.owner.pubkey(), &env.mint, env.seed_id);
        env.vault = get_associated_token_address(&env.treasury, &env.mint);
        let (o, b) = (env.owner.pubkey(), env.beneficiary.pubkey());
        env.owner_token = env.create_ata(&o, &env.mint.clone()).await;
        env.beneficiary_token = env.create_ata(&b, &env.mint.clone()).await;
        env.mint_to(&env.owner_token.clone(), 100_000_000).await;
        env
    }

    /// Fresh env with an initialized and funded treasury.
    async fn funded() -> Self {
        let mut env = Env::new().await;
        let params = env.default_params().await;
        let guardian = Some(env.guardian.pubkey());
        env.initialize(params, guardian).await.unwrap();
        env.deposit(LIFETIME * 2).await.unwrap();
        env
    }

    async fn send(
        &mut self,
        ixs: &[Instruction],
        extra: &[&Keypair],
    ) -> Result<(), BanksClientError> {
        let bh = self.ctx.get_new_latest_blockhash().await.unwrap();
        let mut signers: Vec<&Keypair> = vec![&self.owner];
        signers.extend_from_slice(extra);
        let tx = Transaction::new_signed_with_payer(ixs, Some(&self.owner.pubkey()), &signers, bh);
        self.ctx.banks_client.process_transaction(tx).await
    }

    async fn now(&mut self) -> i64 {
        self.ctx
            .banks_client
            .get_sysvar::<Clock>()
            .await
            .unwrap()
            .unix_timestamp
    }

    async fn warp(&mut self, secs: i64) {
        let mut clock: Clock = self.ctx.banks_client.get_sysvar().await.unwrap();
        clock.unix_timestamp += secs;
        self.ctx.set_sysvar(&clock);
    }

    async fn default_params(&mut self) -> PolicyParams {
        PolicyParams {
            per_tx_cap: PER_TX,
            daily_cap: DAILY,
            lifetime_cap: LIFETIME,
            expires_at: self.now().await + 30 * DAY,
        }
    }

    async fn create_mint(&mut self, freeze: Option<Pubkey>) -> Pubkey {
        let mint = Keypair::new();
        let rent = self.ctx.banks_client.get_rent().await.unwrap();
        let ixs = [
            system_instruction::create_account(
                &self.owner.pubkey(),
                &mint.pubkey(),
                rent.minimum_balance(spl_token::state::Mint::LEN),
                spl_token::state::Mint::LEN as u64,
                &spl_token::id(),
            ),
            spl_token::instruction::initialize_mint2(
                &spl_token::id(),
                &mint.pubkey(),
                &self.owner.pubkey(),
                freeze.as_ref(),
                6,
            )
            .unwrap(),
        ];
        self.send(&ixs, &[&mint]).await.unwrap();
        mint.pubkey()
    }

    async fn create_ata(&mut self, wallet: &Pubkey, mint: &Pubkey) -> Pubkey {
        let ixs = [
            spl_associated_token_account::instruction::create_associated_token_account(
                &self.owner.pubkey(),
                wallet,
                mint,
                &spl_token::id(),
            ),
        ];
        self.send(&ixs, &[]).await.unwrap();
        get_associated_token_address(wallet, mint)
    }

    /// A token account owned by `owner` that is NOT the associated token account.
    async fn create_plain_token_account(&mut self, owner: &Pubkey, mint: &Pubkey) -> Pubkey {
        let acct = Keypair::new();
        let rent = self.ctx.banks_client.get_rent().await.unwrap();
        let ixs = [
            system_instruction::create_account(
                &self.owner.pubkey(),
                &acct.pubkey(),
                rent.minimum_balance(spl_token::state::Account::LEN),
                spl_token::state::Account::LEN as u64,
                &spl_token::id(),
            ),
            spl_token::instruction::initialize_account3(
                &spl_token::id(),
                &acct.pubkey(),
                mint,
                owner,
            )
            .unwrap(),
        ];
        self.send(&ixs, &[&acct]).await.unwrap();
        acct.pubkey()
    }

    async fn mint_to(&mut self, dest: &Pubkey, amount: u64) {
        let ixs = [spl_token::instruction::mint_to(
            &spl_token::id(),
            &self.mint,
            dest,
            &self.owner.pubkey(),
            &[],
            amount,
        )
        .unwrap()];
        self.send(&ixs, &[]).await.unwrap();
    }

    async fn balance(&mut self, account: &Pubkey) -> u64 {
        let a = self
            .ctx
            .banks_client
            .get_account(*account)
            .await
            .unwrap()
            .expect("token account exists");
        spl_token::state::Account::unpack(&a.data).unwrap().amount
    }

    async fn state(&mut self) -> Treasury {
        let a = self
            .ctx
            .banks_client
            .get_account(self.treasury)
            .await
            .unwrap()
            .expect("treasury exists");
        Treasury::try_deserialize(&mut a.data.as_slice()).unwrap()
    }

    fn init_ix(
        &self,
        mint: Pubkey,
        treasury: Pubkey,
        agent: Pubkey,
        params: PolicyParams,
        guardian: Option<Pubkey>,
    ) -> Instruction {
        ix(
            prog::accounts::Initialize {
                owner: self.owner.pubkey(),
                agent,
                beneficiary: self.beneficiary.pubkey(),
                mint,
                treasury,
                vault: get_associated_token_address(&treasury, &mint),
                token_program: spl_token::id(),
                associated_token_program: spl_associated_token_account::id(),
                system_program: system_program::id(),
            },
            prog::instruction::Initialize {
                seed_id: self.seed_id,
                params,
                guardian,
            },
        )
    }

    async fn initialize(
        &mut self,
        params: PolicyParams,
        guardian: Option<Pubkey>,
    ) -> Result<(), BanksClientError> {
        let i = self.init_ix(
            self.mint,
            self.treasury,
            self.agent.pubkey(),
            params,
            guardian,
        );
        self.send(&[i], &[]).await
    }

    async fn deposit(&mut self, amount: u64) -> Result<(), BanksClientError> {
        let i = ix(
            prog::accounts::Deposit {
                owner: self.owner.pubkey(),
                treasury: self.treasury,
                mint: self.mint,
                owner_token: self.owner_token,
                vault: self.vault,
                token_program: spl_token::id(),
            },
            prog::instruction::Deposit { amount },
        );
        self.send(&[i], &[]).await
    }

    fn spend_ix_with(
        &self,
        agent: Pubkey,
        mint: Pubkey,
        vault: Pubkey,
        to: Pubkey,
        amount: u64,
        nonce: u64,
    ) -> Instruction {
        ix(
            prog::accounts::Spend {
                agent,
                treasury: self.treasury,
                mint,
                vault,
                beneficiary_token: to,
                token_program: spl_token::id(),
            },
            prog::instruction::Spend { amount, nonce },
        )
    }

    async fn spend(&mut self, amount: u64, nonce: u64) -> Result<(), BanksClientError> {
        let i = self.spend_ix_with(
            self.agent.pubkey(),
            self.mint,
            self.vault,
            self.beneficiary_token,
            amount,
            nonce,
        );
        let agent = self.agent.insecure_clone();
        self.send(&[i], &[&agent]).await
    }

    async fn next_spend(&mut self, amount: u64) -> Result<(), BanksClientError> {
        let n = self.state().await.next_nonce;
        self.spend(amount, n).await
    }

    fn owner_vault_accounts(&self, owner: Pubkey, to: Pubkey) -> prog::accounts::OwnerVault {
        prog::accounts::OwnerVault {
            owner,
            treasury: self.treasury,
            mint: self.mint,
            vault: self.vault,
            owner_token: to,
            token_program: spl_token::id(),
        }
    }

    async fn withdraw(&mut self, amount: u64) -> Result<(), BanksClientError> {
        let i = ix(
            self.owner_vault_accounts(self.owner.pubkey(), self.owner_token),
            prog::instruction::Withdraw { amount },
        );
        self.send(&[i], &[]).await
    }

    fn owner_action(&self, owner: Pubkey) -> prog::accounts::OwnerAction {
        prog::accounts::OwnerAction {
            owner,
            treasury: self.treasury,
        }
    }

    fn guardian_action(&self, authority: Pubkey) -> prog::accounts::GuardianAction {
        prog::accounts::GuardianAction {
            authority,
            treasury: self.treasury,
        }
    }
}

#[tokio::test]
async fn happy_path_initialize_deposit_spend() {
    let mut env = Env::funded().await;
    let s = env.state().await;
    assert_eq!(s.owner, env.owner.pubkey());
    assert_eq!(s.agent, env.agent.pubkey());
    assert_eq!(s.beneficiary, env.beneficiary.pubkey());
    assert_eq!(s.guardian, Some(env.guardian.pubkey()));
    assert_eq!(s.version, prog::TREASURY_VERSION);
    assert_eq!(env.balance(&env.vault.clone()).await, LIFETIME * 2);

    env.spend(500_000, 0).await.unwrap();
    assert_eq!(env.balance(&env.beneficiary_token.clone()).await, 500_000);
    let s = env.state().await;
    assert_eq!(
        (s.next_nonce, s.daily_spent, s.lifetime_spent),
        (1, 500_000, 500_000)
    );
}

#[tokio::test]
async fn initialize_rejects_invalid_configuration() {
    let mut env = Env::new().await;
    let mut p = env.default_params().await;
    p.per_tx_cap = DAILY + 1;
    assert_code(env.initialize(p, None).await, INVALID_CAPS);

    let mut p = env.default_params().await;
    p.expires_at = env.now().await;
    assert_code(env.initialize(p, None).await, INVALID_EXPIRY);

    let p = env.default_params().await;
    let i = env.init_ix(env.mint, env.treasury, env.owner.pubkey(), p, None);
    assert_code(env.send(&[i], &[]).await, INVALID_AUTHORITY);

    // Guardian may not be the agent.
    assert_code(
        env.initialize(p, Some(env.agent.pubkey())).await,
        INVALID_AUTHORITY,
    );

    // Mint with a freeze authority that is not allow-listed (M1).
    let freezable = env.create_mint(Some(env.owner.pubkey())).await;
    let t = treasury_pda(&env.owner.pubkey(), &freezable, env.seed_id);
    let i = env.init_ix(freezable, t, env.agent.pubkey(), p, None);
    assert_code(env.send(&[i], &[]).await, MINT_NOT_ALLOWED);
}

#[tokio::test]
async fn reinitialization_is_rejected() {
    let mut env = Env::funded().await;
    let p = env.default_params().await;
    // System program: account already in use.
    assert_code(env.initialize(p, None).await, 0);
}

#[tokio::test]
async fn replayed_or_skipped_nonce_rejected() {
    let mut env = Env::funded().await;
    env.spend(1, 0).await.unwrap();
    assert_code(env.spend(1, 0).await, INVALID_NONCE);
    assert_code(env.spend(1, 2).await, INVALID_NONCE);
    env.spend(1, 1).await.unwrap();
}

#[tokio::test]
async fn per_transaction_cap_and_zero_amount() {
    let mut env = Env::funded().await;
    assert_code(env.spend(PER_TX + 1, 0).await, PER_TX_LIMIT);
    assert_code(env.spend(0, 0).await, PER_TX_LIMIT);
    env.spend(PER_TX, 0).await.unwrap();
}

#[tokio::test]
async fn daily_cap_uses_decaying_allowance() {
    let mut env = Env::funded().await;
    // Raise the lifetime cap so only the daily allowance is under test.
    let mut p = env.default_params().await;
    p.lifetime_cap = 100 * DAILY;
    let i = ix(
        env.owner_action(env.owner.pubkey()),
        prog::instruction::UpdatePolicy { params: p },
    );
    env.send(&[i], &[]).await.unwrap();
    env.next_spend(PER_TX).await.unwrap();
    env.next_spend(PER_TX).await.unwrap();
    assert_code(env.next_spend(1).await, DAILY_LIMIT);

    // H2: no boundary burst. One second later only ~DAILY/86_400 has refilled.
    env.warp(1).await;
    assert_code(env.next_spend(100).await, DAILY_LIMIT);

    // Half a day refills half the daily cap, and no more.
    env.warp(DAY / 2).await;
    env.next_spend(DAILY / 2).await.unwrap();
    assert_code(env.next_spend(100).await, DAILY_LIMIT);

    // A full day of inactivity refills the whole cap (but never above it).
    env.warp(3 * DAY).await;
    env.next_spend(PER_TX).await.unwrap();
    env.next_spend(PER_TX).await.unwrap();
    assert_code(env.next_spend(1).await, DAILY_LIMIT);
}

#[tokio::test]
async fn lifetime_cap_enforced() {
    let mut env = Env::funded().await;
    for _ in 0..2 {
        env.next_spend(PER_TX).await.unwrap();
        env.next_spend(PER_TX).await.unwrap();
        env.warp(DAY).await;
    }
    assert_eq!(env.state().await.lifetime_spent, LIFETIME);
    assert_code(env.next_spend(1).await, LIFETIME_LIMIT);
}

#[tokio::test]
async fn expiry_blocks_spend_until_policy_update() {
    let mut env = Env::funded().await;
    env.warp(31 * DAY).await;
    assert_code(env.next_spend(1).await, EXPIRED);

    let p = env.default_params().await; // expires 30 days from the new now
    let i = ix(
        env.owner_action(env.owner.pubkey()),
        prog::instruction::UpdatePolicy { params: p },
    );
    env.send(&[i], &[]).await.unwrap();
    env.next_spend(1).await.unwrap();
}

#[tokio::test]
async fn update_policy_is_owner_only_and_validated() {
    let mut env = Env::funded().await;
    let attacker = Keypair::new();
    let mut p = env.default_params().await;
    p.per_tx_cap = DAILY;
    let i = ix(
        env.owner_action(attacker.pubkey()),
        prog::instruction::UpdatePolicy { params: p },
    );
    assert_code(env.send(&[i], &[&attacker]).await, CONSTRAINT_HAS_ONE);

    p.daily_cap = LIFETIME + 1;
    let i = ix(
        env.owner_action(env.owner.pubkey()),
        prog::instruction::UpdatePolicy { params: p },
    );
    assert_code(env.send(&[i], &[]).await, INVALID_CAPS);

    p.daily_cap = DAILY;
    let i = ix(
        env.owner_action(env.owner.pubkey()),
        prog::instruction::UpdatePolicy { params: p },
    );
    env.send(&[i], &[]).await.unwrap();
    env.next_spend(DAILY).await.unwrap();
}

#[tokio::test]
async fn wrong_agent_and_wrong_beneficiary_rejected() {
    let mut env = Env::funded().await;
    let attacker = Keypair::new();
    let i = env.spend_ix_with(
        attacker.pubkey(),
        env.mint,
        env.vault,
        env.beneficiary_token,
        1,
        0,
    );
    assert_code(env.send(&[i], &[&attacker]).await, CONSTRAINT_HAS_ONE);

    let agent = env.agent.insecure_clone();
    let i = env.spend_ix_with(agent.pubkey(), env.mint, env.vault, env.owner_token, 1, 0);
    assert_code(env.send(&[i], &[&agent]).await, CONSTRAINT_TOKEN_OWNER);
}

#[tokio::test]
async fn wrong_mint_rejected() {
    let mut env = Env::funded().await;
    let other = env.create_mint(None).await;
    let o = env.owner.pubkey();
    let b = env.beneficiary.pubkey();
    let other_owner_token = env.create_ata(&o, &other).await;
    let other_benef_token = env.create_ata(&b, &other).await;

    let agent = env.agent.insecure_clone();
    let i = env.spend_ix_with(agent.pubkey(), other, env.vault, other_benef_token, 1, 0);
    assert_code(env.send(&[i], &[&agent]).await, CONSTRAINT_HAS_ONE);

    let mut accts = env.owner_vault_accounts(o, other_owner_token);
    accts.mint = other;
    let i = ix(accts, prog::instruction::Withdraw { amount: 1 });
    assert_code(env.send(&[i], &[]).await, CONSTRAINT_HAS_ONE);
}

#[tokio::test]
async fn spoofed_vaults_rejected() {
    let mut env = Env::funded().await;
    let agent = env.agent.insecure_clone();

    // A non-ATA token account that the treasury PDA owns.
    let treasury = env.treasury;
    let mint = env.mint;
    let fake = env.create_plain_token_account(&treasury, &mint).await;
    let i = env.spend_ix_with(agent.pubkey(), env.mint, fake, env.beneficiary_token, 1, 0);
    assert_code(env.send(&[i], &[&agent]).await, CONSTRAINT_ASSOCIATED);

    // Another treasury's vault (same owner and mint, different seed_id):
    // rejected by the associated_token::authority owner check.
    let other_t = treasury_pda(&env.owner.pubkey(), &env.mint, 99);
    let p = env.default_params().await;
    let mut i = env.init_ix(env.mint, other_t, env.agent.pubkey(), p, None);
    i.data = prog::instruction::Initialize {
        seed_id: 99,
        params: p,
        guardian: None,
    }
    .data();
    env.send(&[i], &[]).await.unwrap();
    let other_vault = get_associated_token_address(&other_t, &env.mint);
    let i = env.spend_ix_with(
        agent.pubkey(),
        env.mint,
        other_vault,
        env.beneficiary_token,
        1,
        0,
    );
    assert_code(env.send(&[i], &[&agent]).await, CONSTRAINT_TOKEN_OWNER);
    // Vaults are untouched.
    assert_eq!(env.balance(&env.vault.clone()).await, LIFETIME * 2);
}

#[tokio::test]
async fn owner_withdraws_and_non_owner_cannot() {
    let mut env = Env::funded().await;
    let before = env.balance(&env.owner_token.clone()).await;
    env.withdraw(1_000).await.unwrap();
    assert_eq!(env.balance(&env.owner_token.clone()).await, before + 1_000);
    assert_code(env.withdraw(0).await, INVALID_AMOUNT);

    let attacker = Keypair::new();
    let mint = env.mint;
    let attacker_token = env.create_ata(&attacker.pubkey(), &mint).await;
    let i = ix(
        env.owner_vault_accounts(attacker.pubkey(), attacker_token),
        prog::instruction::Withdraw { amount: 1 },
    );
    assert_code(env.send(&[i], &[&attacker]).await, CONSTRAINT_HAS_ONE);

    // Owner signs, but tries to route funds to someone else's token account.
    let benef = env.beneficiary_token;
    let i = ix(
        env.owner_vault_accounts(env.owner.pubkey(), benef),
        prog::instruction::Withdraw { amount: 1 },
    );
    assert_code(env.send(&[i], &[]).await, CONSTRAINT_TOKEN_OWNER);
}

#[tokio::test]
async fn withdraw_after_revoke_and_expiry_recovers_funds() {
    // C1 regression: owner can always recover funds.
    let mut env = Env::funded().await;
    let i = ix(
        env.guardian_action(env.owner.pubkey()),
        prog::instruction::Revoke {},
    );
    env.send(&[i], &[]).await.unwrap();
    assert_code(env.next_spend(1).await, REVOKED);

    env.warp(365 * DAY).await;
    let vault = env.vault;
    let remaining = env.balance(&vault).await;
    env.withdraw(remaining).await.unwrap();
    assert_eq!(env.balance(&vault).await, 0);
}

#[tokio::test]
async fn rotate_agent_replaces_key_and_clears_revocation() {
    let mut env = Env::funded().await;
    let i = ix(
        env.guardian_action(env.owner.pubkey()),
        prog::instruction::Revoke {},
    );
    env.send(&[i], &[]).await.unwrap();

    let new_agent = Keypair::new();
    let i = ix(
        env.owner_action(env.owner.pubkey()),
        prog::instruction::RotateAgent {
            new_agent: env.beneficiary.pubkey(),
        },
    );
    assert_code(env.send(&[i], &[]).await, INVALID_AUTHORITY);
    let i = ix(
        env.owner_action(env.owner.pubkey()),
        prog::instruction::RotateAgent {
            new_agent: new_agent.pubkey(),
        },
    );
    env.send(&[i], &[]).await.unwrap();

    // Old agent is locked out; new agent spends with the continuing nonce.
    assert_code(env.next_spend(1).await, CONSTRAINT_HAS_ONE);
    env.agent = new_agent;
    env.next_spend(1).await.unwrap();
    assert!(!env.state().await.revoked);
}

#[tokio::test]
async fn guardian_can_pause_and_revoke_but_not_unpause() {
    let mut env = Env::funded().await;
    let guardian = env.guardian.insecure_clone();
    let stranger = Keypair::new();

    let i = ix(
        env.guardian_action(stranger.pubkey()),
        prog::instruction::Pause {},
    );
    assert_code(env.send(&[i], &[&stranger]).await, UNAUTHORIZED);

    let i = ix(
        env.guardian_action(guardian.pubkey()),
        prog::instruction::Pause {},
    );
    env.send(&[i], &[&guardian]).await.unwrap();
    assert_code(env.next_spend(1).await, PAUSED);

    let i = ix(
        env.owner_action(guardian.pubkey()),
        prog::instruction::Unpause {},
    );
    assert_code(env.send(&[i], &[&guardian]).await, CONSTRAINT_HAS_ONE);
    let i = ix(
        env.owner_action(env.owner.pubkey()),
        prog::instruction::Unpause {},
    );
    env.send(&[i], &[]).await.unwrap();
    env.next_spend(1).await.unwrap();

    let i = ix(
        env.guardian_action(guardian.pubkey()),
        prog::instruction::Revoke {},
    );
    env.send(&[i], &[&guardian]).await.unwrap();
    assert_code(env.next_spend(1).await, REVOKED);

    // Owner removes the guardian; it can no longer act.
    let i = ix(
        env.owner_action(env.owner.pubkey()),
        prog::instruction::SetGuardian { guardian: None },
    );
    env.send(&[i], &[]).await.unwrap();
    let i = ix(
        env.guardian_action(guardian.pubkey()),
        prog::instruction::Pause {},
    );
    assert_code(env.send(&[i], &[&guardian]).await, UNAUTHORIZED);
}

#[tokio::test]
async fn close_drains_vault_and_returns_rent() {
    let mut env = Env::funded().await;
    env.spend(PER_TX, 0).await.unwrap();
    let vault = env.vault;
    let remaining = env.balance(&vault).await;
    let owner_token = env.owner_token;
    let tokens_before = env.balance(&owner_token).await;

    let close = |owner: Pubkey, env: &Env| {
        ix(
            prog::accounts::Close {
                owner,
                treasury: env.treasury,
                mint: env.mint,
                vault: env.vault,
                owner_token: env.owner_token,
                token_program: spl_token::id(),
            },
            prog::instruction::Close {},
        )
    };
    let attacker = Keypair::new();
    let i = close(attacker.pubkey(), &env);
    assert_code(env.send(&[i], &[&attacker]).await, CONSTRAINT_HAS_ONE);

    let lamports_before = env
        .ctx
        .banks_client
        .get_balance(env.owner.pubkey())
        .await
        .unwrap();
    let i = close(env.owner.pubkey(), &env);
    env.send(&[i], &[]).await.unwrap();

    assert_eq!(env.balance(&owner_token).await, tokens_before + remaining);
    assert!(env
        .ctx
        .banks_client
        .get_account(env.treasury)
        .await
        .unwrap()
        .is_none());
    assert!(env
        .ctx
        .banks_client
        .get_account(vault)
        .await
        .unwrap()
        .is_none());
    let lamports_after = env
        .ctx
        .banks_client
        .get_balance(env.owner.pubkey())
        .await
        .unwrap();
    assert!(lamports_after > lamports_before, "rent returned to owner");

    // The closed treasury can no longer be used.
    assert_code(env.next_spend_after_close().await, ACCOUNT_NOT_INITIALIZED);
}

impl Env {
    async fn next_spend_after_close(&mut self) -> Result<(), BanksClientError> {
        self.spend(1, 1).await
    }
}
