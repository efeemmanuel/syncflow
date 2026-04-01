import random
import string
from app.core.redis import redis_client


# generate otp function
def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


# dave the otp to redis
async def save_otp(email: str, otp: str):
    # store in redis, expires in 10 minutes
    await redis_client.setex(f"otp:{email}", 600, otp)



# verify the otp between redis and user input 
async def verify_otp(email: str, otp: str) -> bool:
    stored_otp = await redis_client.get(f"otp:{email}")
    if not stored_otp:
        return False
    if stored_otp != otp:
        return False
    # delete otp after successful verification
    await redis_client.delete(f"otp:{email}")
    return True