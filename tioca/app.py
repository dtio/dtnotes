# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file
import subprocess
import io
import zipfile
import shutil
import uuid
from ipaddress import ip_address
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Initialize the Flask application
app = Flask(__name__)

# Set a secret key for session management (e.g., for flash messages)
app.secret_key = os.environ.get('SECRET_KEY', 'tioCAsuperSecret')

# Define a simple environment variable to show where the app is running
# This helps confirm the container is using the correct configuration

@app.route('/')
def home():
    """
    The main route, which lists created CAs and provides download links.
    """
    cas = []
    instance_folder = app.instance_path
    if os.path.exists(instance_folder):
        for filename in os.listdir(instance_folder):
            if filename.endswith('.crt'):
                cert_path = os.path.join(instance_folder, filename)
                try:
                    with open(cert_path, "rb") as f:
                        cert_data = f.read()
                    cert = x509.load_pem_x509_certificate(cert_data)
                    ca_name = os.path.splitext(filename)[0]
                    cas.append({'name': ca_name, 'filename': filename, 'expiry': cert.not_valid_after_utc})
                except (IOError, ValueError) as e:
                    # Could be a broken cert file, log and skip
                    app.logger.error(f"Could not load certificate {filename}: {e}")

    cas.sort(key=lambda x: x['name'])
    return render_template("index.html", cas=cas)

@app.route('/create_ca', methods=['GET', 'POST'])
def create_ca():
    """
    Handles the creation of a new Certificate Authority.
    GET: Displays the creation form.
    POST: Processes the form data.
    """
    if request.method == 'POST':
        # --- 1. Get Data from Form ---
        common_name = request.form.get('common_name')
        country = request.form.get('country')
        organization = request.form.get('organization')
        validity_days = int(request.form.get('validity_days', 3650))

        # --- 2. Generate Private Key ---
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # --- 3. Build Certificate Subject ---
        subject_attrs = [x509.NameAttribute(NameOID.COMMON_NAME, common_name)]
        if country:
            subject_attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, country))
        if organization:
            subject_attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization))

        subject = issuer = x509.Name(subject_attrs)

        # --- 4. Build and Sign Certificate ---
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(uuid.uuid4().int)
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=validity_days))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(key, hashes.SHA256())
        )

        # --- 5. Serialize Key and Cert to PEM format ---
        key_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)

        # --- 6. Save files to the instance folder ---
        # Sanitize the common name to create a safe filename
        safe_filename = "".join(c for c in common_name if c.isalnum() or c in (' ', '_')).rstrip()
        key_path = os.path.join(app.instance_path, f"{safe_filename}.key")
        cert_path = os.path.join(app.instance_path, f"{safe_filename}.crt")

        try:
            os.makedirs(app.instance_path, exist_ok=True)
            with open(key_path, "wb") as f:
                f.write(key_pem)
            with open(cert_path, "wb") as f:
                f.write(cert_pem)
            flash(f"Successfully created CA '{common_name}'!", 'success')
            flash(f"Key and certificate saved in '{app.instance_path}'.", 'info')
        except IOError as e:
            flash(f"Error saving files: {e}", 'danger')

        return redirect(url_for('home'))

    # For a GET request, just show the form
    return render_template("create_ca.html")

@app.route('/manage_ca/<path:ca_filename>', methods=['GET', 'POST'])
def manage_ca(ca_filename):
    """
    Manages a specific CA.
    GET: Shows signed certs and a form to create a new one.
    POST: Creates and signs a new certificate.
    """
    ca_name = os.path.splitext(ca_filename)[0]
    ca_cert_path = os.path.join(app.instance_path, ca_filename)
    ca_key_path = os.path.join(app.instance_path, f"{ca_name}.key")
    certs_dir = os.path.join(app.instance_path, ca_name, 'certs')

    if not os.path.exists(ca_cert_path) or not os.path.exists(ca_key_path):
        flash(f"CA '{ca_name}' not found.", 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # --- Create a new signed certificate ---
        try:
            # 1. Load CA key and cert
            with open(ca_key_path, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)
            with open(ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())

            # 2. Get data from form
            common_name = request.form.get('common_name')
            sans_str = request.form.get('sans', '')
            validity_days = int(request.form.get('validity_days', 365))

            # 3. Generate new key for the certificate
            new_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

            # 4. Build certificate subject and SANs
            subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
            sans = [x509.DNSName(common_name)]
            if sans_str:
                for san in sans_str.split(','):
                    san = san.strip()
                    if san:
                        try:
                            # Check if it's an IP address
                            sans.append(x509.IPAddress(ip_address(san)))
                        except ValueError:
                            # Otherwise, it's a DNS name
                            sans.append(x509.DNSName(san))

            # 5. Build and sign the new certificate
            new_cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(ca_cert.subject)
                .public_key(new_key.public_key())
                .serial_number(uuid.uuid4().int)
                .not_valid_before(datetime.now(timezone.utc))
                .not_valid_after(datetime.now(timezone.utc) + timedelta(days=validity_days))
                .add_extension(x509.SubjectAlternativeName(sans), critical=False)
                .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
                .sign(ca_key, hashes.SHA256())
            )

            # 6. Serialize the new key and cert
            new_key_pem = new_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            new_cert_pem = new_cert.public_bytes(serialization.Encoding.PEM)

            # 7. Save the files to the server
            safe_filename = "".join(c for c in common_name if c.isalnum() or c in (' ', '_')).rstrip()
            os.makedirs(certs_dir, exist_ok=True)
            with open(os.path.join(certs_dir, f"{safe_filename}.key"), "wb") as f:
                f.write(new_key_pem)
            with open(os.path.join(certs_dir, f"{safe_filename}.crt"), "wb") as f:
                f.write(new_cert_pem)

            flash(f"Successfully signed and saved certificate for '{common_name}'!", 'success')

        except Exception as e:
            flash(f"Error creating certificate: {e}", 'danger')
            app.logger.error(f"Error creating certificate: {e}", exc_info=True)
        return redirect(url_for('manage_ca', ca_filename=ca_filename))

    # --- For GET request, list existing certificates ---
    certificates = []
    if os.path.exists(certs_dir):
        for filename in os.listdir(certs_dir):
            if filename.endswith('.crt'):
                cert_path = os.path.join(certs_dir, filename)
                try:
                    with open(cert_path, "rb") as f:
                        cert = x509.load_pem_x509_certificate(f.read())
                    cert_name = os.path.splitext(filename)[0]
                    certificates.append({'name': cert_name, 'filename': filename, 'expiry': cert.not_valid_after_utc})
                except (IOError, ValueError) as e:
                    app.logger.error(f"Could not load signed certificate {filename}: {e}")

    certificates.sort(key=lambda x: x['name'])
    return render_template("manage_ca.html", ca_name=ca_name, ca_filename=ca_filename, certificates=certificates)

@app.route('/download_ca/<path:filename>')
def download_ca(filename):
    """
    Provides a download link for a given CA certificate.
    """
    return send_from_directory(
        app.instance_path, filename, as_attachment=True
    )

@app.route('/download_cert/<path:ca_filename>/<path:cert_filename>')
def download_cert(ca_filename, cert_filename):
    """Provides a download link for a zip archive containing the certificate and its key."""
    ca_name = os.path.splitext(ca_filename)[0]
    cert_name = os.path.splitext(cert_filename)[0]
    certs_dir = os.path.join(app.instance_path, ca_name, 'certs')

    cert_path = os.path.join(certs_dir, f"{cert_name}.crt")
    key_path = os.path.join(certs_dir, f"{cert_name}.key")

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        flash(f"Certificate or key for '{cert_name}' not found.", 'danger')
        return redirect(url_for('manage_ca', ca_filename=ca_filename))

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(cert_path, arcname=f"{cert_name}.crt")
        zf.write(key_path, arcname=f"{cert_name}.key")
    memory_file.seek(0)

    return send_file(
        memory_file,
        as_attachment=True,
        download_name=f'{cert_name}.zip',
        mimetype='application/zip'
    )


@app.route('/view_ca/<path:filename>')
def view_ca(filename):
    """
    Displays the details of a CA certificate, similar to `openssl x509 -text`.
    """
    cert_path = os.path.join(app.instance_path, filename)
    if not os.path.exists(cert_path):
        flash(f"Certificate '{filename}' not found.", 'danger')
        return redirect(url_for('home'))

    try:
        # Use openssl to get the text representation of the certificate
        result = subprocess.run(
            ['openssl', 'x509', '-in', cert_path, '-noout', '-text'],
            capture_output=True, text=True, check=True
        )
        cert_details = result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        cert_details = f"Error getting certificate details: {e}\nMake sure 'openssl' is installed in the container."

    return render_template("view_ca.html", cert_name=os.path.splitext(filename)[0], cert_details=cert_details)

@app.route('/view_cert/<path:ca_filename>/<path:cert_filename>')
def view_cert(ca_filename, cert_filename):
    """Displays the details of a signed certificate."""
    ca_name = os.path.splitext(ca_filename)[0]
    cert_path = os.path.join(app.instance_path, ca_name, 'certs', cert_filename)

    if not os.path.exists(cert_path):
        flash(f"Certificate '{cert_filename}' not found.", 'danger')
        return redirect(url_for('manage_ca', ca_filename=ca_filename))

    try:
        result = subprocess.run(
            ['openssl', 'x509', '-in', cert_path, '-noout', '-text'],
            capture_output=True, text=True, check=True
        )
        cert_details = result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        cert_details = f"Error getting certificate details: {e}"

    return render_template("view_ca.html", cert_name=os.path.splitext(cert_filename)[0], cert_details=cert_details, ca_filename=ca_filename)

@app.route('/delete_ca/<path:ca_filename>', methods=['POST'])
def delete_ca(ca_filename):
    """Deletes a CA, its key, and all its signed certificates."""
    ca_name = os.path.splitext(ca_filename)[0]
    ca_cert_path = os.path.join(app.instance_path, ca_filename)
    ca_key_path = os.path.join(app.instance_path, f"{ca_name}.key")
    certs_dir = os.path.join(app.instance_path, ca_name)

    try:
        if os.path.exists(ca_cert_path):
            os.remove(ca_cert_path)
        if os.path.exists(ca_key_path):
            os.remove(ca_key_path)
        if os.path.isdir(certs_dir):
            shutil.rmtree(certs_dir)
        flash(f"Successfully deleted CA '{ca_name}' and all its assets.", 'success')
    except OSError as e:
        flash(f"Error deleting CA '{ca_name}': {e}", 'danger')
        app.logger.error(f"Error deleting CA {ca_name}: {e}")

    return redirect(url_for('home'))

@app.route('/delete_cert/<path:ca_filename>/<path:cert_filename>', methods=['POST'])
def delete_cert(ca_filename, cert_filename):
    """Deletes a single signed certificate and its key."""
    ca_name = os.path.splitext(ca_filename)[0]
    cert_name = os.path.splitext(cert_filename)[0]
    cert_path = os.path.join(app.instance_path, ca_name, 'certs', f"{cert_name}.crt")
    key_path = os.path.join(app.instance_path, ca_name, 'certs', f"{cert_name}.key")

    os.remove(cert_path)
    os.remove(key_path)
    flash(f"Successfully deleted certificate '{cert_name}'.", 'success')
    return redirect(url_for('manage_ca', ca_filename=ca_filename))

@app.route('/renew_cert/<path:ca_filename>/<path:cert_filename>', methods=['GET', 'POST'])
def renew_cert(ca_filename, cert_filename):
    """
    Handles the renewal of a signed certificate.
    GET: Displays the renewal form.
    POST: Creates a new certificate with a new expiry date.
    """
    ca_name = os.path.splitext(ca_filename)[0]
    cert_name = os.path.splitext(cert_filename)[0]
    certs_dir = os.path.join(app.instance_path, ca_name, 'certs')

    ca_cert_path = os.path.join(app.instance_path, ca_filename)
    ca_key_path = os.path.join(app.instance_path, f"{ca_name}.key")
    old_cert_path = os.path.join(certs_dir, f"{cert_name}.crt")
    old_key_path = os.path.join(certs_dir, f"{cert_name}.key")

    if not all(os.path.exists(p) for p in [ca_cert_path, ca_key_path, old_cert_path, old_key_path]):
        flash("Required CA or certificate files are missing.", 'danger')
        return redirect(url_for('manage_ca', ca_filename=ca_filename))

    if request.method == 'POST':
        try:
            new_validity_days = int(request.form.get('validity_days'))

            # Load all necessary keys and certs
            with open(ca_key_path, "rb") as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)
            with open(ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())
            with open(old_key_path, "rb") as f:
                old_key = serialization.load_pem_private_key(f.read(), password=None)
            with open(old_cert_path, "rb") as f:
                old_cert = x509.load_pem_x509_certificate(f.read())

            # Build a new certificate with the old details and new expiry
            builder = (
                x509.CertificateBuilder()
                .subject_name(old_cert.subject)
                .issuer_name(ca_cert.subject)
                .public_key(old_key.public_key())
                .serial_number(uuid.uuid4().int) # New serial number
                .not_valid_before(datetime.now(timezone.utc))
                .not_valid_after(datetime.now(timezone.utc) + timedelta(days=new_validity_days))
            )

            # Copy extensions from the old certificate
            for extension in old_cert.extensions:
                builder = builder.add_extension(extension.value, critical=extension.critical)

            new_cert = builder.sign(ca_key, hashes.SHA256())

            # Overwrite the old certificate file
            with open(old_cert_path, "wb") as f:
                f.write(new_cert.public_bytes(serialization.Encoding.PEM))

            flash(f"Successfully renewed certificate '{cert_name}' for {new_validity_days} days.", 'success')
            return redirect(url_for('manage_ca', ca_filename=ca_filename))
        except Exception as e:
            flash(f"Error renewing certificate: {e}", 'danger')
            app.logger.error(f"Error renewing certificate: {e}", exc_info=True)

    # For GET request, show the form
    return render_template("renew_cert.html", ca_filename=ca_filename, cert_filename=cert_filename, cert_name=cert_name)

# This block runs the app with the development server
# when the script is executed directly (e.g., `python app.py`).
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
