SET PROPPI=C:\Users\smaldonado\Documents\proppi

echo "INICIANDO SCRAPPER %PROPPI%"

cmd /k "cd /d %PROPPI%\proppienv\Scripts & activate & cd /d   %PROPPI% & python scrapper.py"

echo "FINALIZANDO SCRAPPER"

PAUSE