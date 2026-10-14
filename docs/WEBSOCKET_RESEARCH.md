# Offline WebSocket / SignalR research

## External reference
The third-party repository Zakaria-laktati/crash-1xbet-monitoring documents a
WebSocket and a SignalR-style `OnCrash` event. This is unverified third-party
code, not an official guarantee of the protocol or endpoint lifetime.

Reference: https://github.com/Zakaria-laktati/crash-1xbet-monitoring

## What our parser does
- Reads **locally supplied** UTF-8 SignalR text frames.
- Splits messages on SignalR's record separator (U+001E).
- Accepts invocation messages with `type=1`, `target=OnCrash`,
  `arguments` containing objects with keys `l` (round ID) and `f`
  (final multiplier).
- Rejects invalid/nonfinite multipliers, duplicate conflicting outcomes.
- Ignores ticks, control frames and unknown event types.

**Interpretation:** An `OnCrash` message typically reports the final result,
not advance knowledge of a future multiplier. A frame timestamp alone does not
prove when the game generated or announced a result.

## Restrictions / privacy
No direct WebSocket connection, token extraction, bypass of access controls,
automated betting, or scraping of private APIs. Do not paste access tokens,
session cookies or signed WebSocket URLs into the repository.

## Next verification
An independently obtained, consented export of network events without secrets
would allow us to validate payload shapes and compare event arrival times.
Record local receipt times separately; never infer predictive power from
after-the-fact labels.
