from passlib.context import CryptContext

#创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#密码加密
def get_password_hash(password):
    return pwd_context.hash(password)

#密码校验，返回一个bool值
def verify_password(plain_password,hashed_password):
    #verify_password(明文,哈希)
    return pwd_context.verify(plain_password, hashed_password)