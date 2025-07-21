from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError
from database.database import get_db
from database import crud, schemas, auth
import os
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    return crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Generate JWT access and refresh tokens for authentication"""
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = auth.create_refresh_token(
        data={"sub": user.email}
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    """Get current user information"""
    return current_user

@router.put("/users/me", response_model=schemas.User)
def update_user_settings(user_data: schemas.UserUpdate, current_user: schemas.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    """Update user settings"""
    return crud.update_user(db=db, user_id=current_user.id, user_data=user_data)

@router.delete("/users/me")
def delete_user_account(current_user: schemas.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    """Delete user account and all associated data"""
    return crud.delete_user(db=db, user_id=current_user.id)

@router.post("/token/refresh", response_model=schemas.Token)
def refresh_access_token(token_data: schemas.TokenRefresh, db: Session = Depends(get_db)):
    """Generate a new access token using a refresh token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the refresh token
        token_data_verified = auth.verify_token(token_data.refresh_token, credentials_exception, token_type="refresh")
        
        # Get the user from the database
        user = db.query(crud.User).filter(crud.User.email == token_data_verified.email).first()
        if user is None:
            raise credentials_exception
        
        # Create new access token
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Create new refresh token
        refresh_token = auth.create_refresh_token(
            data={"sub": user.email}
        )
        
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except JWTError:
        raise credentials_exception


# Send a real password reset email
def send_password_reset_email(email: str, token: str):
    """Send a password reset email using SMTP"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import logging
    
    # Set up logger
    logger = logging.getLogger("drugsy")
    
    # Get email configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL")
    
    # Make sure we have a from_email, fallback to username only if FROM_EMAIL is not set
    if not from_email:
        from_email = smtp_username
    
    # Create reset URL (frontend URL)
    reset_url = f"http://localhost:3000/reset-password?token={token}"
    
    # Log email configuration (without password)
    logger.info(f"Email configuration: Server={smtp_server}, Port={smtp_port}, Username={smtp_username}, From={from_email}")
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset - Drugsy"
    
    # Gmail requires the From address to match the authenticated user
    # So we use the SMTP_USERNAME as From and set Reply-To to our desired FROM_EMAIL
    message["From"] = smtp_username
    message["Reply-To"] = from_email
    message["To"] = email
    
    # Add a custom header for better identification
    message["X-Application"] = "Drugsy Password Reset"
    
    # Create HTML version of the message
    html = f"""
    <html>
      <body>
        <h2>Password Reset Request</h2>
        <p>You have requested to reset your password for your Drugsy account.</p>
        <p>Please click the link below to reset your password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>This link will expire in 24 hours.</p>
        <p>If you did not request a password reset, please ignore this email.</p>
      </body>
    </html>
    """
    
    # Create plain text version of the message
    text = f"""
    Password Reset Request
    
    You have requested to reset your password for your Drugsy account.
    
    Please click the link below to reset your password:
    {reset_url}
    
    This link will expire in 24 hours.
    
    If you did not request a password reset, please ignore this email.
    """
    
    # Attach parts to message
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    
    logger.info(f"Attempting to send password reset email to {email}")
    
    try:
        # Connect to server and send email
        logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        logger.info("Starting TLS connection")
        server.starttls()
        
        logger.info(f"Logging in with username: {smtp_username}")
        server.login(smtp_username, smtp_password)
        
        logger.info(f"Sending email from {from_email} to {email}")
        server.sendmail(from_email, email, message.as_string())
        
        server.quit()
        logger.info(f"✅ SUCCESS: Password reset email sent to {email}")
        print(f"✅ SUCCESS: Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"❌ ERROR: Failed to send password reset email: {str(e)}")
        print(f"❌ ERROR: Failed to send password reset email: {str(e)}")
        
        # Log detailed error information
        if smtp_username is None or smtp_password is None:
            logger.error("❌ ERROR: SMTP credentials are not configured. Check your .env file.")
            print("❌ ERROR: SMTP credentials are not configured. Check your .env file.")
        
        # Fall back to console output for development/testing
        reset_link_message = f"📧 DEV MODE: Password reset link for {email}: {reset_url}"
        logger.info(reset_link_message)
        print(f"\n{reset_link_message}\n")


@router.post("/forgot-password", response_model=Dict[str, str])
def forgot_password(reset_request: schemas.PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Request a password reset token"""
    # Create a password reset token
    token = crud.create_password_reset_token(db, reset_request.email)
    
    # If user exists, send reset email (in background)
    if token:
        background_tasks.add_task(send_password_reset_email, reset_request.email, token)
    
    # Always return success to prevent email enumeration attacks
    return {"message": "If your email is registered, you will receive a password reset link shortly."}


@router.post("/reset-password", response_model=Dict[str, str])
def reset_password(reset_data: schemas.PasswordReset, db: Session = Depends(get_db)):
    """Reset password using a valid token"""
    # Try to reset the password
    success = crud.reset_password(db, reset_data.token, reset_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )
    
    return {"message": "Password has been reset successfully"}
