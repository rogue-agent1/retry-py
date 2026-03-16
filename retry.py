import time, random
class RetryConfig:
    def __init__(s, max_retries=3, base_delay=1.0, max_delay=60.0, backoff="exponential", jitter=True):
        s.max_retries=max_retries; s.base_delay=base_delay; s.max_delay=max_delay
        s.backoff=backoff; s.jitter=jitter
    def delay(s, attempt):
        if s.backoff == "constant": d = s.base_delay
        elif s.backoff == "linear": d = s.base_delay * (attempt + 1)
        elif s.backoff == "exponential": d = s.base_delay * (2 ** attempt)
        else: d = s.base_delay
        d = min(d, s.max_delay)
        if s.jitter: d *= random.uniform(0.5, 1.5)
        return d
class Retry:
    def __init__(s, config=None): s.config = config or RetryConfig(); s.attempts = []
    def execute(s, fn, *args, **kwargs):
        for attempt in range(s.config.max_retries + 1):
            try:
                result = fn(*args, **kwargs)
                s.attempts.append({"attempt": attempt, "success": True})
                return result
            except Exception as e:
                delay = s.config.delay(attempt)
                s.attempts.append({"attempt": attempt, "error": str(e), "delay": delay})
                if attempt == s.config.max_retries: raise
        raise RuntimeError("Max retries exceeded")
def demo():
    random.seed(42); call_count = [0]
    def flaky():
        call_count[0] += 1
        if call_count[0] < 3: raise ConnectionError(f"fail #{call_count[0]}")
        return "success!"
    r = Retry(RetryConfig(max_retries=5, base_delay=0.1))
    result = r.execute(flaky)
    print(f"Result: {result}")
    for a in r.attempts: print(f"  Attempt {a['attempt']}: {'OK' if a.get('success') else a.get('error')}")
    # Show backoff delays
    cfg = RetryConfig(base_delay=1.0)
    delays = [round(cfg.delay(i), 2) for i in range(6)]
    print(f"Exponential backoff delays: {delays}")
if __name__ == "__main__": demo()
