from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.cms import bp
from app.extensions import db
from app.models import Dokument

@bp.route("/<string:kod>")
def view(kod):
    # Restricted pages
    if kod in ['dokumentacja', 'szablony'] and not current_user.is_authenticated:
        flash("Musisz się zalogować, aby uzyskać dostęp do tego zasobu.", "warning")
        return redirect(url_for("auth.login", next=request.url))

    dokument = Dokument.query.filter_by(kod=kod).first()
    if not dokument:
        if current_user.is_authenticated and current_user.is_admin():
            # Auto-create if admin visits non-existent but expected page
            if kod in ['regulamin', 'polityka', 'dokumentacja', 'szablony']:
                tytuly = {
                    'regulamin': 'Regulamin Systemu PZW',
                    'polityka': 'Polityka Prywatności',
                    'dokumentacja': 'Instrukcja Obsługi i Dokumentacja',
                    'szablony': 'Wzory i Szablony Dokumentów'
                }
                tresci = {
                    'regulamin': '### REGULAMIN KORZYSTANIA Z SYSTEMU\n\n1. **Wstęp**\nNiniejszy system jest narzędziem wspomagającym organizację zawodów wędkarskich zgodnie z wytycznymi ZOSW.\n\n2. **Użytkownicy**\nDostęp do panelu administracyjnego mają wyłącznie upoważnieni sędziowie oraz administratorzy koła.\n\n3. **Przetwarzanie Danych**\nDane zawodników (imię, nazwisko, przynależność) są przetwarzane wyłącznie w celu wygenerowania list startowych i klasyfikacji.',
                    'polityka': '### POLITYKA PRYWATNOŚCI (RODO)\n\n1. **Administrator Danych**\nAdministratorem danych osobowych jest właściwe Koło PZW organizujące zawody.\n\n2. **Zakres danych**\nSystem przechowuje: Imię, Nazwisko, Nr Licencji oraz Koło macierzyste zawodnika.\n\n3. **Zgody RODO**\nKażdy zawodnik ma prawo do zastrzeżenia publikacji swoich danych osobowych. W takim przypadku w widoku publicznym (dla gości) zawodnik będzie figurował pod unikalnym numerem (np. Zawodnik#123).',
                    'dokumentacja': '### INSTRUKCJA OBSŁUGI DLA SĘDZIÓW\n\n#### 1. Przygotowanie zawodów\n- Przejdź do zakładki **Zawody** i kliknij **Nowe zawody**.\n- Wypełnij parametry (liczba tur, sektory, dyscyplina).\n- Wybierz sędziego głównego i sekretarza z listy.\n\n#### 2. Dodawanie uczestników\n- Możesz dodać zawodników ręcznie w widoku szczegółów zawodów.\n- Polecamy skorzystać z **Importu CSV** w zakładce Zawodnicy, aby wgrać całą bazę koła naraz.\n\n#### 3. Losowanie stanowisk\n- W zakładce **Stanowiska i Losowanie** możesz automatycznie rozlosować sektory.\n- System wspiera "Zasadę drużynową" (zawodnicy z tej samej drużyny nie trafią do jednego sektora).\n\n#### 4. Wprowadzanie wyników\n- Podczas zawodów sędzia może wpisywać wagę lub punkty bezpośrednio na telefonie.\n- Pamiętaj, aby po każdej turze kliknąć **Zatwierdź wyniki**.\n\n#### 5. Generowanie raportów\n- Po zakończeniu wszystkich tur przejdź do zakładki **Klasyfikacja**.\n- Pobierz gotowy **Protokół PDF** lub **Klasyfikację końcową**.',
                    'szablony': 'W tej sekcji znajdziesz wzory dokumentów potrzebnych do pracy w kole.'
                }
                dokument = Dokument(kod=kod, tytul=tytuly[kod], tresc=tresci[kod])
                db.session.add(dokument)
                db.session.commit()
            else:
                abort(404)
        else:
            abort(404)
    
    if kod == 'szablony':
        return render_template("cms/szablony.html", dokument=dokument)
        
    return render_template("cms/view.html", dokument=dokument)

@bp.route("/<string:kod>/edytuj", methods=["GET", "POST"])
@login_required
def edytuj(kod):
    if not current_user.is_admin():
        abort(403)
        
    dokument = Dokument.query.filter_by(kod=kod).first()
    if not dokument:
        abort(404)
        
    if request.method == "POST":
        dokument.tytul = request.form.get("tytul")
        dokument.tresc = request.form.get("tresc")
        db.session.commit()
        flash(f"Dokument '{dokument.tytul}' został zaktualizowany.", "success")
        return redirect(url_for("cms.view", kod=kod))
        
    return render_template("cms/formularz.html", dokument=dokument)
