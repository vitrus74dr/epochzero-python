# Web Requests

Thousands of services answer questions over HTTP: weather, exchange rates, trivia
questions, GitHub repositories. Your program sends a request to a URL and gets back
JSON. This lesson is about doing that *robustly*, because over a network everything
that can go wrong eventually does.

## 1. Install `requests`

```sh
uv add requests
```

## 2. A first request

```python
import requests

response = requests.get(
    "https://api.github.com/repos/python/cpython",
    timeout=10,
)
response.raise_for_status()
repo = response.json()
print(repo["full_name"], repo["stargazers_count"])
```

Three habits in five lines:

- **`timeout=10`**: give up after 10 seconds. *Without* a timeout, `requests` can wait
  **forever** on a server that accepted the connection and never answers. Every request
  in this course gets a timeout; it's on the pitfall watch.
- **`raise_for_status()`**: HTTP reports failures with a status code (404 not found,
  429 too many requests, 500 server error), but `requests` doesn't treat those as
  errors on its own. This line turns them into an exception.
- **`.json()`**: parses the body into dicts and lists.

Query parameters go in `params=`, which handles the `?a=1&b=2` encoding for you:

```python fragment
requests.get("https://opentdb.com/api.php", params={"amount": 5, "type": "multiple"}, timeout=10)
```

## 3. What can go wrong

```python
import requests

def fetch_json(url: str, **params) -> dict | None:
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        print("The server took too long to answer.")
    except requests.ConnectionError:
        print("Couldn't connect. Are you online?")
    except requests.HTTPError as e:
        print(f"The server said no: {e.response.status_code}")
    except requests.JSONDecodeError:
        print("The answer wasn't valid JSON.")
    return None
```

Each `except` handles one specific failure with a message a person can act on. All of
them inherit from `requests.RequestException`, but catching that alone loses the
detail. Keep the `try` block small (Lesson 1.3): just the network calls.

**Try it:** call `fetch_json` with a misspelled host name (`https://api.githubb.com`),
then with a path that doesn't exist (`https://api.github.com/nope`). Which `except` fires
for each?

## 4. Reading an API's own error codes

Some APIs return HTTP 200 ("OK") even when the request failed, and put the real
status inside the JSON. Open Trivia DB is one: its answer always has a `response_code`.

| `response_code` | Meaning |
|---|---|
| 0 | success |
| 1 | not enough questions for your query |
| 2 | an invalid parameter |
| 5 | rate limited: wait about 5 seconds between requests |

Check the code **before** you touch the data. When it isn't 0, the answer may not even
have a `results` key (a rate-limited answer is `{"response_code": 5, "result": []}`), so
`data["results"]` would crash with a `KeyError`.

## 5. Your turn (W4.2.a)

In `week4/t4.2-requests/weather.py`, use the free Open-Meteo API (no key needed):

```text
https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current=temperature_2m,wind_speed_10m
```

- Pass latitude and longitude with `params=`, and set a `timeout=`.
- Call `raise_for_status()`, then print the current temperature and wind speed from the
  JSON. Open the URL in your browser first to see the shape of the answer.
- Handle `Timeout` and `ConnectionError` with friendly messages. (Turn off your Wi-Fi to
  try the second one.)

Show the tutor both a success and a handled failure.

## Pitfalls

- A request without `timeout=`.
- Skipping `raise_for_status()`, then parsing an error page as data.
- A bare `except:` (or `except Exception:`) around network code.
- Requests in a tight loop. Public APIs rate-limit you; be polite.
