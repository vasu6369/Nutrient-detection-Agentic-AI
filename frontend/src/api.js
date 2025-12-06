// src/api.js
const BASE = "http://127.0.0.1:8000"; // backend base

export async function postChatForm(form) {
    const res = await fetch(`${BASE}/chat`, {
        method: "POST",
        body: form,
    });
    if (!res.ok) throw new Error("Server error: " + res.status);
    return res.json();
}

export async function postChatJSON(json) {
    const res = await fetch(`${BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(json),
    });
    if (!res.ok) throw new Error("Server error: " + res.status);
    return res.json();
}
