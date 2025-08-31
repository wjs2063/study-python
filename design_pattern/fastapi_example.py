import uvicorn
from fastapi import FastAPI
from aiomisc.circuit_breaker import cutout, CircuitBreaker
import asyncio

app = FastAPI()

circuit_breaker = CircuitBreaker(error_ratio=1, response_time=100, recovery_time=5, broken_time=5,
                                 passing_time=5)


async def call_external_with_fail():
    raise Exception("External call with fail")

async def call_external_with_success():
    return "success"

@app.get("/fail")
async def root():
    try:
        print(circuit_breaker._counters.call_count,circuit_breaker._counters.call_broken)
        print(circuit_breaker.state)
        print(circuit_breaker.recovery_ratio)
        print(circuit_breaker.get_state_delay())
        response = await circuit_breaker.call_async(call_external_with_fail)
    except Exception as e:
        return {"status": "fail"}
    return {"status": response}

@app.get("/success")
async def success_root():
    print(circuit_breaker._counters.call_count, circuit_breaker._counters.call_broken)
    print(circuit_breaker.state)
    print(circuit_breaker.recovery_ratio)
    print(circuit_breaker.get_state_delay())
    response = await circuit_breaker.call_async(call_external_with_success)
    return {"status": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
