# Jwt

```bash
openssl genpkey -algorithm RSA -out jwt_private.key -pkeyopt rsa_keygen_bits:2048
```

```bash
openssl rsa -pubout -in private.key -out public.key
```