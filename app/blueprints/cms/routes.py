from flask import render_template, redirect, url_for, flash, request, abort, send_file
from flask_login import login_required, current_user
from datetime import datetime
import io
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
    
    # Lawyer-grade content definitions
    tytuly = {
        'regulamin': 'Regulamin Korzystania z Systemu Obsługi Zawodów',
        'polityka': 'Polityka Prywatności i Obowiązek Informacyjny (RODO)',
        'dokumentacja': 'Instrukcja Obsługi i Dokumentacja Techniczna',
        'szablony': 'Centrum Szablonów i Wzorów Dokumentów'
    }
    
    tresci = {
        'regulamin': """### REGULAMIN SYSTEMU

**§1. Postanowienia ogólne**
1. Niniejszy system informatyczny (dalej: "System") stanowi niezależne narzędzie wspomagające organizację zawodów wędkarskich.
2. Właścicielem i administratorem technicznym Systemu jest podmiot prywatny. System nie jest oficjalnym narzędziem Polskiego Związku Wędkarskiego (PZW).
3. Korzystanie z Systemu oznacza akceptację niniejszego regulaminu.

**§2. Zasady korzystania**
1. Dostęp do panelu administracyjnego posiadają wyłącznie zarejestrowani Sędziowie oraz Administratorzy.
2. Użytkownik zobowiązany jest do wprowadzania danych zgodnych ze stanem faktycznym.
3. Zabrania się wykorzystywania Systemu do celów niezgodnych z prawem.

**§3. Odpowiedzialność**
1. Administrator Systemu nie ponosi odpowiedzialności za błędy w wynikach wynikające z błędnie wprowadzonych danych przez sędziów.
2. System jest projektem hobbystycznym i jest dostarczany w stanie "takim, jaki jest" (as-is), bez gwarancji nieprzerwanej dostępności.
""",
        'polityka': """### POLITYKA PRYWATNOŚCI (RODO)

**1. Administrator Danych Osobowych**
Administratorem danych osobowych (ADO) przetwarzanych w systemie jest właściwe Koło PZW lub Okręg PZW organizujący dane zawody sportowe.

**2. Cel i Podstawa Przetwarzania**
Dane zawodników przetwarzane są na podstawie:
- Art. 6 ust. 1 lit. a RODO (dobrowolna zgoda) – w zakresie publikacji imienia i nazwiska w publicznych zestawieniach.
- Art. 6 ust. 1 lit. f RODO (prawnie uzasadniony interes) – w celu organizacji zawodów, losowania stanowisk i prowadzenia dokumentacji sportowej.

**3. Zakres danych**
System przetwarza: Imię, Nazwisko, Nr licencji sportowej, Przynależność do koła/klubu.

**4. Prawa osób, których dane dotyczą**
Każdy zawodnik ma prawo do:
- Wglądu w swoje dane.
- Sprostowania danych.
- Usunięcia danych ("prawo do bycia zapomnianym").
- Cofnięcia zgody na publikację danych w dowolnym momencie (co skutkuje anonimizacją w widokach publicznych).

**5. Anonimizacja**
W przypadku braku zgody RODO, system automatycznie maskuje dane zawodnika dla użytkowników niezalogowanych, używając identyfikatora technicznego.
""",
        'dokumentacja': """### INSTRUKCJA OBSŁUGI DLA SĘDZIÓW

#### I. KONFIGURACJA POCZĄTKOWA
Aby rozpocząć pracę, administrator powinien uzupełnić **Słowniki**:
1. **Łowiska**: Dodaj akweny, na których rozgrywane są zawody.
2. **Dyscypliny**: Wybierz odpowiedni system punktacji (Wagowy, Punktowy lub Karpiowy).
3. **Ryby**: Zdefiniuj wymiary ochronne i punktację za mm (wymagane dla spinningu/muchy).

#### II. ZARZĄDZANIE ZAWODNIKAMI
- Możesz dodawać zawodników pojedynczo lub masowo przez **Import CSV**.
- Pamiętaj o zaznaczeniu pola **Zgoda RODO** – od tego zależy, czy zawodnik będzie widoczny dla kibiców.

#### III. PRZEBIEG ZAWODÓW
1. **Tworzenie**: Ustal liczbę tur i sektorów.
2. **Losowanie**: Użyj automatu. System dba, aby członkowie tej samej drużyny byli w różnych sektorach.
3. **Wyniki**: Wpisuj wyniki na bieżąco. System przelicza punkty sektorowe automatycznie zgodnie z regulaminem ZOSW.
4. **Zakończenie**: Po ostatniej turze wygeneruj klasyfikację końcową.

#### IV. EKSPORT DANYCH
Z każdej podstrony klasyfikacji możesz pobrać profesjonalny **Protokół PDF** wygenerowany przez silnik WeasyPrint.

#### V. USTAWIENIA I PREFERENCJE
- W zakładce **Ustawienia konta** możesz zdefiniować swoje ulubione wartości domyślne.
- System zapamięta Twoją domyślną dyscyplinę, liczbę sektorów, tur oraz ulubionych sędziów.
- Dzięki temu tworzenie nowych zawodów sprowadza się do wpisania nazwy i wybrania daty.
""",
        'szablony': 'W tej sekcji znajdziesz wzory dokumentów potrzebnych do pracy w kole.'
    }

    if not dokument:
        if current_user.is_authenticated and current_user.is_admin():
            if kod in tytuly:
                dokument = Dokument(kod=kod, tytul=tytuly[kod], tresc=tresci[kod])
                db.session.add(dokument)
                db.session.commit()
            else:
                abort(404)
        else:
            abort(404)
    else:
        # Aktualizujemy treść jeśli jest stara lub placeholderem
        if current_user.is_authenticated and current_user.is_admin():
             if "Wstęp" in dokument.tresc or "Treść w przygotowaniu" in dokument.tresc:
                 dokument.tresc = tresci.get(kod, dokument.tresc)
                 dokument.tytul = tytuly.get(kod, dokument.tytul)
                 db.session.commit()
    
    if kod == 'szablony':
        return render_template("cms/szablony.html", dokument=dokument)
        
    return render_template("cms/view.html", dokument=dokument)

@bp.route("/rodo-pdf")
@login_required
def download_rodo_pdf():
    """Generuje gotową do druku papierową zgodę RODO."""
    rendered_html = render_template("cms/rodo_pdf.html", data_generowania=datetime.now())
    try:
        from weasyprint import HTML
        pdf_file = HTML(string=rendered_html).write_pdf()
        return send_file(
            io.BytesIO(pdf_file),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="oswiadczenie_rodo_zawodnik.pdf"
        )
    except Exception as e:
        flash(f"Błąd generowania dokumentu: {str(e)}", "danger")
        return redirect(url_for("cms.view", kod="szablony"))

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
