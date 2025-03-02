# realadvisor
Descubre las mejores oportunidades inmobiliarias con nuestro sistema de recomendación. Analiza datos clave, estima rentabilidad y riesgos, y recibe informes detallados para decisiones inteligentes.

### TODO

- DONE informe: cambiar nombre del merged.pdf y añadir mensaje
- informe: Eliminar el NAN del titulo
- informe y datos: Añadir link a imagenes
- informe: Añadir agencia
- informe: corregir exceso de decimales en la rentabilidad 
- datos: pasar el creation date a lambda
- DONE env: Eliminar chat_id del repo
- datos: encriptar datos
- env: eliminar datos del repo
- datos: actualizar datos precios
- env: añadir como servicio en htpc
- informe: enviar cada informe en markdown por telegram



This error occurs because the Docker daemon isn't running or you don't have the proper permissions. Let's fix this with these steps:

1. First, check if Docker service is running:
```bash
sudo systemctl status docker
```

2. If it's not running, start it:
```bash
sudo systemctl start docker
```

3. Add your user to the docker group to avoid using sudo for docker commands:
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Verify your user is in the docker group
groups
```

4. Apply the changes:
```bash
# Reload groups without logging out
newgrp docker
```

If you still get the error, try these additional steps:

1. Restart the Docker daemon:
```bash
sudo systemctl restart docker
```

2. Make sure the Docker socket has the correct permissions:
```bash
sudo chmod 666 /var/run/docker.sock
```

After making these changes, try running your script again:
```bash
./run.sh
```

If you're still having issues, you might need to log out and log back in for the group changes to take effect completely.

Note: The `chmod 666` solution is temporary and will reset after a system restart. The proper solution is ensuring your user is in the docker group.


---




If Git is not ignoring a file despite it being listed in `.gitignore`, it's likely because the file was already tracked by Git before being added to `.gitignore`. The `.gitignore` file only works for untracked files.

To fix this, you need to:

1. First, remove the file from Git's tracking (but keep it on your disk):
```bash
git rm --cached report/reports/property_report_Eixample.html
```

2. Make sure your `.gitignore` entry is correct (it looks fine in your case):
```gitignore
report/reports/property_report_Eixample.html
```

3. Commit the changes:
```bash
git add .gitignore
git commit -m "Stop tracking property_report_Eixample.html"
```

After these steps, Git will stop tracking the file, and it will be properly ignored. The file will remain on your local system but won't be included in future commits.

Note: If you want to ignore all HTML files in that directory, you could use a pattern instead:
```gitignore
report/reports/*.html
```
