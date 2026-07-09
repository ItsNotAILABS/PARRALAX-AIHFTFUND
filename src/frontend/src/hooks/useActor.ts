import {
  useActor as _useActor,
  useInternetIdentity,
} from "@caffeineai/core-infrastructure";
import { createActor } from "../backend";

function hasIdentity(identityState: unknown): boolean {
  const state = identityState as Record<string, unknown> | null | undefined;
  if (!state) return false;

  if (typeof state.isAuthenticated === "boolean") return state.isAuthenticated;
  if (state.identity) return true;
  if (state.principal) return true;
  if (state.userPrincipal) return true;
  return false;
}

export function useActor(): any {
  const actorState = _useActor(createActor) as any;
  const identityState = useInternetIdentity() as unknown;

  return {
    ...actorState,
    isAuthenticated: hasIdentity(identityState) || Boolean(actorState?.actor),
  };
}
