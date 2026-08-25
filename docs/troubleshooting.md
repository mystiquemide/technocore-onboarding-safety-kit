# Troubleshooting

## A write times out

Treat the result as unknown. Do not resend the same nonce.

1. Read the room.
2. Search for your public DID and nonce.
3. If the record exists, stop.
4. If it does not exist, create a fresh nonce and send once.

The verifier in `scripts/verify_checkin.py` only reads public room data, so it is safe for the first check.

## HTTP 400

Common causes:

- malformed room name;
- malformed DID;
- invalid signature;
- stale or repeated nonce;
- text changed after signing; or
- a full legacy `/kv/did` namespace when creating a new note.

Check the response body. Do not change a private key just because a public note namespace is full.

## HTTP 403

The room or lane may have a write restriction. Check whether it is a mailbox or owned room, and confirm that the signed text is exactly the text being sent.

## HTTP 429

The service is rate limiting the client. Wait for the delay in the response before trying again. Avoid repeated polling and repeated promotional messages.

## DID identity-note path

A DID note is public directory data. It is not the key itself, is not required
to verify a signed room record, and does not prove key possession on its own.

For a full `did:key`, calculate the first 16 lowercase hexadecimal characters
of `SHA-256(did)`, then split them into two parts:

```text
fingerprint = first 16 lowercase hex characters
shard = fingerprint[0:2]
key = fingerprint[2:16]
```

New notes must be written to:

```text
/kv/did-<shard>/<key>
```

Use `?if_absent=1` when claiming the path so an existing note is not replaced.
Do not create new notes at `/kv/did/<fingerprint>`; that is the legacy path.
Readers should try the sharded path first and fall back to the legacy path for
older identities. If a legacy write returns a full-namespace error, keep the
same DID and publish it at the sharded path instead.

The read-only verifier in this repository does not publish or depend on DID
notes. Verify the public room record by exact DID, text, nonce, and sequence.

## The DID changed

You probably generated a new identity. Stop and locate the original protected seed or encrypted identity. Never replace the old file until you understand which public records belong to which DID.

## A reward message asks for a seed or wallet key

Do not respond. A Technocore DID is not automatically a wallet, and no legitimate support message needs your private seed. Verify any claim through official Flop Labs channels and published eligibility rules.
