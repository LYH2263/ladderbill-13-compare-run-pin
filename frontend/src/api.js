export async function request(path, method = 'GET', body) {
  const opts = { method, headers: {} }
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  }
  const r = await fetch(path, opts)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
export const getJSON = (path) => request(path, 'GET')
export const postJSON = (path, body) => request(path, 'POST', body ?? {})
export const putJSON = (path, body) => request(path, 'PUT', body ?? {})
export const deleteJSON = (path) => request(path, 'DELETE')
