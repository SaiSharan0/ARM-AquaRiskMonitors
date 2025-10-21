from app import create_app

app = create_app()

with app.test_client() as c:
    # Visit login to set session
    resp_get = c.get('/login')
    print('GET /login:', resp_get.status_code)

    # Attempt login with default admin credentials
    resp_post = c.post('/login', data={'email':'admin@aquarisk.org','password':'Admin@123'}, follow_redirects=True)
    print('POST /login ->', resp_post.status_code)

    # Now test protected pages
    for path in ['/report', '/map', '/admin']:
        r = c.get(path, follow_redirects=False)
        print(f'GET {path}:', r.status_code, r.headers.get('Location'))
        if r.status_code >= 500:
            print('--- BODY START ---')
            print(r.data[:500])
            print('--- BODY END ---')
