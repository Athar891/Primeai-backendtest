async def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


async def test_create_task_success(client, user_token):
    resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Finish Assignment", "description": "wrap up", "status": "todo"},
        headers=await auth_headers(user_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Finish Assignment"
    assert data["status"] == "todo"


async def test_create_task_empty_title_returns_422(client, user_token):
    resp = await client.post("/api/v1/tasks", json={"title": ""}, headers=await auth_headers(user_token))
    assert resp.status_code == 422


async def test_create_task_invalid_status_returns_422(client, user_token):
    resp = await client.post(
        "/api/v1/tasks", json={"title": "x", "status": "bogus"}, headers=await auth_headers(user_token)
    )
    assert resp.status_code == 422


async def test_create_task_without_auth_returns_401(client):
    resp = await client.post("/api/v1/tasks", json={"title": "x"})
    assert resp.status_code == 401


async def test_full_crud_lifecycle(client, user_token):
    headers = await auth_headers(user_token)

    create_resp = await client.post("/api/v1/tasks", json={"title": "Lifecycle task"}, headers=headers)
    task_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Lifecycle task"

    update_resp = await client.put(f"/api/v1/tasks/{task_id}", json={"status": "done"}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "done"

    delete_resp = await client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert delete_resp.status_code == 204

    get_after_delete = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert get_after_delete.status_code == 404


async def test_get_nonexistent_task_returns_404(client, user_token):
    resp = await client.get("/api/v1/tasks/999999", headers=await auth_headers(user_token))
    assert resp.status_code == 404


async def test_update_nonexistent_task_returns_404(client, user_token):
    resp = await client.put(
        "/api/v1/tasks/999999", json={"title": "nope"}, headers=await auth_headers(user_token)
    )
    assert resp.status_code == 404


async def test_delete_nonexistent_task_returns_404(client, user_token):
    resp = await client.delete("/api/v1/tasks/999999", headers=await auth_headers(user_token))
    assert resp.status_code == 404


async def test_empty_task_list_returns_zero_total(client, user_token):
    resp = await client.get("/api/v1/tasks", headers=await auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.json() == {"total": 0, "skip": 0, "limit": 20, "items": []}


async def test_filter_by_status(client, user_token):
    headers = await auth_headers(user_token)
    await client.post("/api/v1/tasks", json={"title": "todo task", "status": "todo"}, headers=headers)
    await client.post("/api/v1/tasks", json={"title": "done task", "status": "done"}, headers=headers)

    resp = await client.get("/api/v1/tasks?status=done", headers=headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "done task"


async def test_search_by_title(client, user_token):
    headers = await auth_headers(user_token)
    await client.post("/api/v1/tasks", json={"title": "Finish Assignment"}, headers=headers)
    await client.post("/api/v1/tasks", json={"title": "Buy groceries"}, headers=headers)

    resp = await client.get("/api/v1/tasks?search=assignment", headers=headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Finish Assignment"


async def test_pagination_limit(client, user_token):
    headers = await auth_headers(user_token)
    for i in range(3):
        await client.post("/api/v1/tasks", json={"title": f"task {i}"}, headers=headers)

    resp = await client.get("/api/v1/tasks?limit=2&skip=0", headers=headers)
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2

    resp2 = await client.get("/api/v1/tasks?limit=2&skip=2", headers=headers)
    assert len(resp2.json()["items"]) == 1
