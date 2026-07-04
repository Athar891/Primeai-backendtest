async def test_non_admin_blocked_from_users_list(client, user_token):
    resp = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403


async def test_admin_can_list_users(client, admin_token, user_token):
    resp = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    emails = {u["email"] for u in resp.json()}
    assert "admin@example.com" in emails
    assert "jane@example.com" in emails


async def test_user_cannot_access_other_users_task(client, user_token, admin_token):
    create_resp = await client.post(
        "/api/v1/tasks", json={"title": "Admin only task"}, headers={"Authorization": f"Bearer {admin_token}"}
    )
    task_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert get_resp.status_code == 403

    delete_resp = await client.delete(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert delete_resp.status_code == 403


async def test_admin_can_access_any_users_task(client, user_token, admin_token):
    create_resp = await client.post(
        "/api/v1/tasks", json={"title": "User task"}, headers={"Authorization": f"Bearer {user_token}"}
    )
    task_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


async def test_user_list_only_shows_own_tasks(client, user_token, admin_token):
    await client.post("/api/v1/tasks", json={"title": "Admin task"}, headers={"Authorization": f"Bearer {admin_token}"})
    await client.post("/api/v1/tasks", json={"title": "User task"}, headers={"Authorization": f"Bearer {user_token}"})

    resp = await client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {user_token}"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "User task"


async def test_admin_list_shows_all_tasks(client, user_token, admin_token):
    await client.post("/api/v1/tasks", json={"title": "Admin task"}, headers={"Authorization": f"Bearer {admin_token}"})
    await client.post("/api/v1/tasks", json={"title": "User task"}, headers={"Authorization": f"Bearer {user_token}"})

    resp = await client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.json()["total"] == 2


async def test_admin_list_includes_task_owner_details(client, user_token, admin_token):
    await client.post("/api/v1/tasks", json={"title": "User task"}, headers={"Authorization": f"Bearer {user_token}"})

    resp = await client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    owners_by_title = {item["title"]: item["owner"] for item in resp.json()["items"]}

    owner = owners_by_title["User task"]
    assert owner is not None
    assert owner["email"] == "jane@example.com"
    assert owner["role"] == "user"


async def test_user_list_does_not_expose_owner_details(client, user_token):
    await client.post("/api/v1/tasks", json={"title": "My task"}, headers={"Authorization": f"Bearer {user_token}"})

    resp = await client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    assert resp.json()["items"][0]["owner"] is None


async def test_admin_single_task_read_includes_owner(client, user_token, admin_token):
    create_resp = await client.post(
        "/api/v1/tasks", json={"title": "User task"}, headers={"Authorization": f"Bearer {user_token}"}
    )
    task_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["owner"]["email"] == "jane@example.com"
