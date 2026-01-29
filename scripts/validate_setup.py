import asyncio
import sys
from rich.console import Console
from rich.table import Table
from app.core.config import settings
from app.adapters.telegram import send_message
from app.adapters.google_sheets import sheets_manager

console = Console()

async def check_env_vars() -> bool:
    required_vars = [
        "VAPI_PRIVATE_KEY", "VAPI_PUBLIC_KEY", "VAPI_WEBHOOK_SECRET",
        "VAPI_SECRET_TOKEN", "TELEGRAM_BOT_TOKEN", "ADMIN_CHAT_ID",
        "GOOGLE_CREDENTIALS_JSON", "SPREADSHEET_ID"
    ]
    
    missing = []
    for var in required_vars:
        val = getattr(settings, var, None)
        if not val:
            missing.append(var)
            
    if missing:
        console.print(f"[bold red]❌ Missing required environment variables:[/bold red] {', '.join(missing)}")
        return False
    
    console.print("[bold green]✅ Environment variables present[/bold green]")
    return True

async def check_vapi_connection() -> bool:
    try:
        import httpx
        headers = {"Authorization": f"Bearer {settings.VAPI_PRIVATE_KEY}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.vapi.ai/assistant", headers=headers)
            
        if resp.status_code == 200:
            console.print("[bold green]✅ Vapi API connection successful[/bold green]")
            return True
        else:
            console.print(f"[bold red]❌ Vapi API failed:[/bold red] {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        console.print(f"[bold red]❌ Vapi check error:[/bold red] {e}")
        return False

async def check_google_sheets() -> bool:
    try:
        # Try to read a small range
        range_name = f"{settings.GOOGLE_SHEET_NAME}!A1:A1"
        await sheets_manager.read_leads(settings.SPREADSHEET_ID, range_name)
        console.print("[bold green]✅ Google Sheets connection successful[/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]❌ Google Sheets error:[/bold red] {e}")
        return False

async def check_telegram() -> bool:
    try:
        if not settings.TELEGRAM_BOT_TOKEN or not settings.ADMIN_CHAT_ID:
            console.print("[yellow]⚠️ Telegram not configured, skipping[/yellow]")
            return True
            
        # Send silent message
        await send_message("🔍 Validating system setup... (Test Message)")
        console.print("[bold green]✅ Telegram message sent[/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]❌ Telegram error:[/bold red] {e}")
        return False

async def main_async():
    console.print("[bold blue]Starting Pre-deployment Validation...[/bold blue]")
    
    table = Table(title="Validation Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", justify="center")

    results = []
    
    # 1. Env Vars
    if await check_env_vars():
        table.add_row("Environment", "✅")
        results.append(True)
    else:
        table.add_row("Environment", "❌")
        results.append(False)

    # 2. Vapi
    if await check_vapi_connection():
         table.add_row("Vapi API", "✅")
         results.append(True)
    else:
         table.add_row("Vapi API", "❌")
         results.append(False)

    # 3. Sheets
    if await check_google_sheets():
        table.add_row("Google Sheets", "✅")
        results.append(True)
    else:
        table.add_row("Google Sheets", "❌")
        results.append(False)
        
    # 4. Telegram
    if await check_telegram():
        table.add_row("Telegram", "✅")
        results.append(True)
    else:
        table.add_row("Telegram", "❌")
        results.append(False)

    console.print(table)
    
    if all(results):
        console.print("\n[bold green]🎉 System is ready for deployment![/bold green]")
        sys.exit(0)
    else:
        console.print("\n[bold red]💥 System validation failed! Check errors above.[/bold red]")
        sys.exit(1)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
