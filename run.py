import click
from werkzeug.security import generate_password_hash
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()


@app.cli.command("create-admin")
@click.argument("email")
@click.argument("haslo")
def create_admin(email, haslo):
    """Tworzy konto administratora."""
    from app.extensions import db
    from app.models import Uzytkownik

    if Uzytkownik.query.filter_by(email=email).first():
        click.echo("Użytkownik z tym emailem już istnieje.")
        return
    admin = Uzytkownik(
        email=email.lower(),
        haslo_hash=generate_password_hash(haslo),
        rola="admin",
        aktywny=True,
    )
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Admin {email} utworzony.")
