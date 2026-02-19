"""Main CLI entry point for AVP."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from avp import AVPClient
from avp.backends import FileBackend, MemoryBackend

console = Console()


def get_default_vault_path() -> Path:
    """Get default vault path."""
    return Path.home() / ".avp" / "vault.enc"


def create_client(vault: str, password: str) -> AVPClient:
    """Create AVP client with file backend."""
    vault_path = Path(vault)
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    backend = FileBackend(str(vault_path), password)
    return AVPClient(backend)


@click.group()
@click.version_option(version="0.1.0", prog_name="avp")
def cli():
    """
    AVP - Agent Vault Protocol CLI

    Secure credential management for AI agents.

    \b
    Quick start:
      avp init                    # Initialize a new vault
      avp store mykey myvalue     # Store a credential
      avp get mykey               # Retrieve a credential
      avp list                    # List all credentials
    """
    pass


@cli.command()
@click.option("--vault", "-v", default=None, help="Path to vault file")
@click.option("--password", "-p", prompt=True, hide_input=True,
              confirmation_prompt=True, help="Vault password")
def init(vault: Optional[str], password: str):
    """Initialize a new AVP vault."""
    vault_path = Path(vault) if vault else get_default_vault_path()

    if vault_path.exists():
        console.print(f"[yellow]Warning:[/yellow] Vault already exists at {vault_path}")
        if not click.confirm("Overwrite existing vault?"):
            raise click.Abort()

    vault_path.parent.mkdir(parents=True, exist_ok=True)

    # Create and initialize vault
    backend = FileBackend(str(vault_path), password)
    client = AVPClient(backend)
    session = client.authenticate(workspace="default")
    client.close()

    console.print(Panel(
        f"[green]Vault initialized successfully![/green]\n\n"
        f"Location: {vault_path}\n"
        f"Workspace: default",
        title="AVP Vault Created"
    ))


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--vault", "-v", default=None, help="Path to vault file")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option("--workspace", "-w", default="default", help="Workspace name")
def store(key: str, value: str, vault: Optional[str], password: str, workspace: str):
    """Store a credential in the vault."""
    vault_path = str(Path(vault) if vault else get_default_vault_path())

    client = create_client(vault_path, password)
    session = client.authenticate(workspace=workspace)

    client.store(session.session_id, key, value.encode())
    client.close()

    console.print(f"[green]✓[/green] Stored credential: [bold]{key}[/bold]")


@cli.command("get")
@click.argument("key")
@click.option("--vault", "-v", default=None, help="Path to vault file")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option("--workspace", "-w", default="default", help="Workspace name")
@click.option("--quiet", "-q", is_flag=True, help="Output only the value")
def get_credential(key: str, vault: Optional[str], password: str, workspace: str, quiet: bool):
    """Retrieve a credential from the vault."""
    vault_path = str(Path(vault) if vault else get_default_vault_path())

    client = create_client(vault_path, password)
    session = client.authenticate(workspace=workspace)

    try:
        result = client.retrieve(session.session_id, key)
        value = result.value.decode()

        if quiet:
            click.echo(value)
        else:
            console.print(f"[bold]{key}[/bold]: {value}")
    except Exception as e:
        console.print(f"[red]Error:[/red] Credential '{key}' not found")
        sys.exit(1)
    finally:
        client.close()


@cli.command("list")
@click.option("--vault", "-v", default=None, help="Path to vault file")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option("--workspace", "-w", default="default", help="Workspace name")
def list_credentials(vault: Optional[str], password: str, workspace: str):
    """List all credentials in the vault."""
    vault_path = str(Path(vault) if vault else get_default_vault_path())

    client = create_client(vault_path, password)
    session = client.authenticate(workspace=workspace)

    result = client.list_secrets(session.session_id)
    client.close()

    if not result.secrets:
        console.print("[dim]No credentials stored.[/dim]")
        return

    table = Table(title=f"Credentials in workspace: {workspace}")
    table.add_column("Key", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Created", style="dim")

    for secret in result.secrets:
        table.add_row(
            secret.name,
            str(getattr(secret, 'version', 1)),
            getattr(secret, 'created_at', '-')
        )

    console.print(table)


@cli.command()
@click.argument("key")
@click.option("--vault", "-v", default=None, help="Path to vault file")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option("--workspace", "-w", default="default", help="Workspace name")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete(key: str, vault: Optional[str], password: str, workspace: str, force: bool):
    """Delete a credential from the vault."""
    vault_path = str(Path(vault) if vault else get_default_vault_path())

    if not force:
        if not click.confirm(f"Delete credential '{key}'?"):
            raise click.Abort()

    client = create_client(vault_path, password)
    session = client.authenticate(workspace=workspace)

    result = client.delete(session.session_id, key)
    client.close()

    if result.deleted:
        console.print(f"[green]✓[/green] Deleted credential: [bold]{key}[/bold]")
    else:
        console.print(f"[red]Error:[/red] Credential '{key}' not found")
        sys.exit(1)


@cli.command()
@click.argument("key")
@click.argument("new_value")
@click.option("--vault", "-v", default=None, help="Path to vault file")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option("--workspace", "-w", default="default", help="Workspace name")
def rotate(key: str, new_value: str, vault: Optional[str], password: str, workspace: str):
    """Rotate a credential with version tracking."""
    vault_path = str(Path(vault) if vault else get_default_vault_path())

    client = create_client(vault_path, password)
    session = client.authenticate(workspace=workspace)

    try:
        client.rotate(session.session_id, key, new_value.encode())
        console.print(f"[green]✓[/green] Rotated credential: [bold]{key}[/bold]")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to rotate '{key}': {e}")
        sys.exit(1)
    finally:
        client.close()


@cli.command()
@click.option("--vault", "-v", default=None, help="Path to vault file")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
def info(vault: Optional[str], password: str):
    """Show vault information."""
    vault_path = Path(vault) if vault else get_default_vault_path()

    if not vault_path.exists():
        console.print(f"[red]Error:[/red] No vault found at {vault_path}")
        console.print("Run 'avp init' to create a new vault.")
        sys.exit(1)

    client = create_client(str(vault_path), password)
    session = client.authenticate(workspace="default")
    result = client.list_secrets(session.session_id)
    client.close()

    size = vault_path.stat().st_size
    size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} bytes"

    console.print(Panel(
        f"[bold]Vault Path:[/bold] {vault_path}\n"
        f"[bold]Size:[/bold] {size_str}\n"
        f"[bold]Credentials:[/bold] {len(result.secrets)}",
        title="AVP Vault Info"
    ))


@cli.command()
@click.argument("source")
@click.option("--vault", "-v", default=None, help="Path to vault file")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option("--workspace", "-w", default="default", help="Workspace name")
@click.option("--format", "-f", "fmt", type=click.Choice(["json", "env", "dotenv"]),
              default="json", help="Source format")
def import_credentials(source: str, vault: Optional[str], password: str,
                       workspace: str, fmt: str):
    """Import credentials from a file."""
    import json

    vault_path = str(Path(vault) if vault else get_default_vault_path())
    source_path = Path(source)

    if not source_path.exists():
        console.print(f"[red]Error:[/red] Source file not found: {source}")
        sys.exit(1)

    client = create_client(vault_path, password)
    session = client.authenticate(workspace=workspace)

    count = 0
    with open(source_path) as f:
        if fmt == "json":
            data = json.load(f)
            for key, value in data.items():
                if isinstance(value, str):
                    client.store(session.session_id, key, value.encode())
                    count += 1
        else:  # env or dotenv
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip().strip('"').strip("'")
                    client.store(session.session_id, key.strip(), value.encode())
                    count += 1

    client.close()
    console.print(f"[green]✓[/green] Imported {count} credentials from {source}")


@cli.command("export")
@click.argument("destination")
@click.option("--vault", "-v", default=None, help="Path to vault file")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option("--workspace", "-w", default="default", help="Workspace name")
@click.option("--format", "-f", "fmt", type=click.Choice(["json", "env", "dotenv"]),
              default="json", help="Export format")
def export_credentials(destination: str, vault: Optional[str], password: str,
                       workspace: str, fmt: str):
    """Export credentials to a file."""
    import json

    vault_path = str(Path(vault) if vault else get_default_vault_path())
    dest_path = Path(destination)

    client = create_client(vault_path, password)
    session = client.authenticate(workspace=workspace)

    result = client.list_secrets(session.session_id)

    credentials = {}
    for secret in result.secrets:
        try:
            value = client.retrieve(session.session_id, secret.name)
            credentials[secret.name] = value.value.decode()
        except Exception:
            pass

    client.close()

    with open(dest_path, "w") as f:
        if fmt == "json":
            json.dump(credentials, f, indent=2)
        else:  # env or dotenv
            for key, value in credentials.items():
                f.write(f'{key}="{value}"\n')

    console.print(f"[green]✓[/green] Exported {len(credentials)} credentials to {destination}")
    console.print(f"[yellow]Warning:[/yellow] Exported file contains sensitive data!")


if __name__ == "__main__":
    cli()
