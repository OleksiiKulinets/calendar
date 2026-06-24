from alembic import op
import sqlalchemy as sa


revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("telegram_chat_id", sa.BigInteger()),
        sa.Column("name", sa.String(255)),
        sa.Column("timezone", sa.String(100)),
        sa.Column("default_city", sa.String(255)),
        sa.Column("default_country", sa.String(255)),
        sa.Column("default_duration_minutes", sa.Integer(), server_default="60"),
        sa.Column("training_data_consent", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "google_accounts",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("google_email", sa.String(255), nullable=False),
        sa.Column("access_token_encrypted", sa.Text()),
        sa.Column("refresh_token_encrypted", sa.Text()),
        sa.Column("token_expires_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "calendars",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("google_calendar_id", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255)),
        sa.Column("timezone", sa.String(100)),
        sa.Column("is_default", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "saved_locations",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255)),
        sa.Column("aliases_json", sa.JSON()),
        sa.Column("formatted_address", sa.Text()),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("google_place_id", sa.String(255)),
        sa.Column("google_maps_url", sa.Text()),
        sa.Column("directions_url", sa.Text()),
        sa.Column("arrival_instructions_text", sa.Text()),
        sa.Column("arrival_instructions_enabled", sa.Boolean(), server_default="0"),
        sa.Column("is_active", sa.Boolean(), server_default="1"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "event_templates",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255)),
        sa.Column("trigger_phrases_json", sa.JSON()),
        sa.Column("title_template", sa.Text()),
        sa.Column("event_format", sa.String(100)),
        sa.Column("duration_minutes", sa.Integer()),
        sa.Column("description_template", sa.Text()),
        sa.Column(
            "saved_location_id",
            sa.BigInteger(),
            sa.ForeignKey("saved_locations.id", ondelete="SET NULL"),
        ),
        sa.Column("create_google_meet", sa.Boolean(), server_default="0"),
        sa.Column("settings_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "event_drafts",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(50)),
        sa.Column("source_message_id", sa.BigInteger()),
        sa.Column("source_text", sa.Text()),
        sa.Column("parsed_data_json", sa.JSON()),
        sa.Column("confidence", sa.Float()),
        sa.Column("status", sa.String(50)),
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "calendar_id",
            sa.BigInteger(),
            sa.ForeignKey("calendars.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("google_event_id", sa.String(255)),
        sa.Column("title", sa.String(500)),
        sa.Column("start_at", sa.DateTime()),
        sa.Column("end_at", sa.DateTime()),
        sa.Column("timezone", sa.String(100)),
        sa.Column("event_format", sa.String(100)),
        sa.Column("description", sa.Text()),
        sa.Column("external_conference_url", sa.Text()),
        sa.Column("google_meet_url", sa.Text()),
        sa.Column("google_event_url", sa.Text()),
        sa.Column("status", sa.String(50)),
        sa.Column("source_type", sa.String(50)),
        sa.Column("source_message_id", sa.BigInteger()),
        sa.Column(
            "saved_location_id",
            sa.BigInteger(),
            sa.ForeignKey("saved_locations.id", ondelete="SET NULL"),
        ),
        sa.Column("last_synced_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "event_locations",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "event_id",
            sa.BigInteger(),
            sa.ForeignKey("events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("raw_value", sa.Text()),
        sa.Column("name", sa.String(255)),
        sa.Column("formatted_address", sa.Text()),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("google_place_id", sa.String(255)),
        sa.Column("google_maps_url", sa.Text()),
        sa.Column("directions_url", sa.Text()),
        sa.Column("is_confirmed", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "event_reminders",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "event_id",
            sa.BigInteger(),
            sa.ForeignKey("events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reminder_minutes", sa.Integer()),
        sa.Column("planned_at", sa.DateTime()),
        sa.Column("sent_at", sa.DateTime()),
        sa.Column("last_checked_at", sa.DateTime()),
        sa.Column("status", sa.String(50)),
        sa.Column("attempts", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "processed_telegram_updates",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("telegram_update_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_message_id", sa.BigInteger()),
        sa.Column("status", sa.String(50)),
        sa.Column("processed_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "ai_processing_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
        ),
        sa.Column(
            "event_draft_id",
            sa.BigInteger(),
            sa.ForeignKey("event_drafts.id", ondelete="SET NULL"),
        ),
        sa.Column("source_type", sa.String(50)),
        sa.Column("provider", sa.String(100)),
        sa.Column("model", sa.String(255)),
        sa.Column("prompt_version", sa.String(100)),
        sa.Column("parser_version", sa.String(100)),
        sa.Column("input_metadata_json", sa.JSON()),
        sa.Column("output_json", sa.JSON()),
        sa.Column("processing_time_ms", sa.Integer()),
        sa.Column("estimated_cost", sa.Numeric(10, 6)),
        sa.Column("status", sa.String(50)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "training_samples",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
        ),
        sa.Column(
            "event_draft_id",
            sa.BigInteger(),
            sa.ForeignKey("event_drafts.id", ondelete="SET NULL"),
        ),
        sa.Column("anonymized_input_json", sa.JSON()),
        sa.Column("model_output_json", sa.JSON()),
        sa.Column("confirmed_output_json", sa.JSON()),
        sa.Column("corrections_json", sa.JSON()),
        sa.Column("is_approved", sa.Boolean(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("training_samples")
    op.drop_table("ai_processing_logs")
    op.drop_table("processed_telegram_updates")
    op.drop_table("event_reminders")
    op.drop_table("event_locations")
    op.drop_table("events")
    op.drop_table("event_drafts")
    op.drop_table("event_templates")
    op.drop_table("saved_locations")
    op.drop_table("calendars")
    op.drop_table("google_accounts")
    op.drop_table("users")