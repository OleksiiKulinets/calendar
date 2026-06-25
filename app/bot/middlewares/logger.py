async def log_update(update, context):
    user = update.effective_user
    text = update.effective_message.text if update.effective_message else None

    print(f"[MSG] {user.id} @{user.username}: {text}")