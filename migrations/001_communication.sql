-- Communication-owned persistence contract.
-- The service does not own database provisioning; this migration defines its records.
CREATE TABLE IF NOT EXISTS communication_conversations (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    professional_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'closed')),
    created_at TEXT NOT NULL,
    closed_at TEXT
);
CREATE TABLE IF NOT EXISTS communication_messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES communication_conversations(id),
    sender_id TEXT NOT NULL,
    sender_type TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS communication_calls (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES communication_conversations(id),
    caller_id TEXT NOT NULL,
    recipient_id TEXT NOT NULL,
    provider_call_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    ended_at TEXT
);
CREATE INDEX IF NOT EXISTS communication_messages_conversation_idx
    ON communication_messages(conversation_id, created_at);
