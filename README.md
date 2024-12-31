# realadvisor
Descubre las mejores oportunidades inmobiliarias con nuestro sistema de recomendación. Analiza datos clave, estima rentabilidad y riesgos, y recibe informes detallados para decisiones inteligentes.




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
