import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
const root=new URL("../",import.meta.url);
const rust=fs.readFileSync(new URL("src/lib.rs",root),"utf8");
const anchor=fs.readFileSync(new URL("Anchor.toml",root),"utf8");
test("source includes hard guards and account checks",()=>{
 for(const fragment of [
  "require!(!t.revoked","require!(now < t.expires_at","nonce == t.next_nonce",
  "daily <= t.daily_cap","lifetime <= t.lifetime_cap","has_one = mint",
  "token::transfer_checked", "pub fn withdraw","pub fn revoke","beneficiary.key().as_ref()",
  "mint.key().as_ref()"
 ])assert.ok(rust.includes(fragment),fragment);
});
test("deployment ID stays explicitly blocked until configured",()=>{
 assert.ok(anchor.includes("11111111111111111111111111111111"));
 assert.ok(rust.includes('declare_id!("11111111111111111111111111111111")'));
});
