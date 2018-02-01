from OpenSSL.crypto import (FILETYPE_PEM, dump_certificate, dump_privatekey,
                            load_pkcs12)


def generate_pems(cert, password, out_dir, **kw):
    """
        function generates (converts) .pem certificate and .pem 
        private key from .p12 certificate and password   

        params:   
            cert [str] - .p12 certificate full path   
            password [str] - .p12 certificate password   
            out_dir [str] - output directory full path   

        optional keyword params:   
            cert_name [str] - generated certificate name (incl extension .pem)   
            key_name [str] - generated certificate name (incl extension .pem)
    """
    cert_path = os.path.join(out_dir, kw.pop("cert_name", "certificate.pem"))
    key_path = os.path.join(out_dir, kw.pop("key_name", "privatekey.pem"))

    with open(cert, 'rb') as stream:
        p12file = stream.read()

    p12file = load_pkcs12(p12file, password)
    pem_cert = dump_certificate(FILETYPE_PEM, p12file.get_certificate())
    pem_key = dump_privatekey(FILETYPE_PEM, p12file.get_privatekey())

    with open(cert_path, 'wb') as stream:
        stream.write(pem_cert + pem_key)

    with open(key_path, 'wb') as stream:
        stream.write(pem_key)

    return cert_path, key_path
