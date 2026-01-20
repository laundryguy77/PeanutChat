Phase 1: Critical Security Fixes - Implementation Plan                         
                                                                                
 Overview                                                                       
                                                                                
 Fix 4 critical security vulnerabilities in PeanutChat that could allow         
 unauthorized access or data exposure.                                          
                                                                                
 ---                                                                            
 Task 1.1: Fix CORS Configuration                                               
                                                                                
 Files to modify:                                                               
 - app/config.py - Add CORS_ORIGINS config variable                             
 - app/main.py - Update CORS middleware to use config                           
 - .env.template - Document new variable                                        
                                                                                
 Changes:                                                                       
                                                                                
 1. In app/config.py (after line 67), add:                                      
 # CORS settings                                                                
 CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")   
                                                                                
 2. In app/main.py (lines 18-25), change from:                                  
 app.add_middleware(                                                            
     CORSMiddleware,                                                            
     allow_origins=["*"],                                                       
     allow_credentials=True,                                                    
     allow_methods=["*"],                                                       
     allow_headers=["*"],                                                       
 )                                                                              
 To:                                                                            
 app.add_middleware(                                                            
     CORSMiddleware,                                                            
     allow_origins=config.CORS_ORIGINS,                                         
     allow_credentials=True,                                                    
     allow_methods=["*"],                                                       
     allow_headers=["*"],                                                       
 )                                                                              
                                                                                
 3. In .env.template, add:                                                      
 # CORS origins (comma-separated, e.g.,                                         
 "http://localhost:8080,https://example.com")                                   
 CORS_ORIGINS=http://localhost:8080                                             
                                                                                
 ---                                                                            
 Task 1.2: Fix Cookie Security                                                  
                                                                                
 Files to modify:                                                               
 - app/config.py - Add COOKIE_SECURE config variable                            
 - app/routers/auth.py - Update cookie settings (lines 32-39 and 63-70)         
 - .env.template - Document new variable                                        
                                                                                
 Changes:                                                                       
                                                                                
 1. In app/config.py (after CORS_ORIGINS), add:                                 
 # Cookie security (set to true in production with HTTPS)                       
 COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"          
                                                                                
 2. In app/routers/auth.py, update both set_cookie calls (lines 32-39 and       
 63-70):                                                                        
 response.set_cookie(                                                           
     key="access_token",                                                        
     value=access_token,                                                        
     httponly=True,                                                             
     secure=config.COOKIE_SECURE,                                               
     samesite="lax",                                                            
     max_age=60 * 60 * 24                                                       
 )                                                                              
                                                                                
 3. Add import at top of app/routers/auth.py:                                   
 from app import config                                                         
                                                                                
 4. In .env.template, add:                                                      
 # Cookie secure flag (set to true in production with HTTPS)                    
 COOKIE_SECURE=false                                                            
                                                                                
 ---                                                                            
 Task 1.3: Add JWT Secret Startup Warning                                       
                                                                                
 Files to modify:                                                               
 - app/main.py - Add startup event with warning                                 
                                                                                
 Changes:                                                                       
                                                                                
 In app/main.py, add a startup event handler:                                   
 @app.on_event("startup")                                                       
 async def startup_security_check():                                            
     if config.JWT_SECRET ==                                                    
 "change-this-in-production-use-a-long-random-string":                          
         logger.warning("SECURITY WARNING: Using default JWT_SECRET! Set        
 JWT_SECRET environment variable for production.")                              
                                                                                
 ---                                                                            
 Task 1.4: Add Auth to Legacy Endpoints                                         
                                                                                
 Files to modify:                                                               
 - app/routers/chat.py - Update legacy /history endpoints (lines 716-733)       
                                                                                
 Changes:                                                                       
                                                                                
 1. Update GET /history (lines 716-723):                                        
 @router.get("/history")                                                        
 async def get_chat_history(request: Request, user: UserResponse =              
 Depends(require_auth)):                                                        
     """Get chat history for current session (legacy)"""                        
     conv_id = request.headers.get("X-Conversation-ID", "default")              
     conv = conversation_store.get(conv_id, user_id=user.id)                    
     if not conv:                                                               
         return {"history": []}                                                 
     return {"history": conversation_store.get_messages_for_api(conv_id)}       
                                                                                
 2. Update DELETE /history (lines 726-733):                                     
 @router.delete("/history")                                                     
 async def clear_chat_history(request: Request, user: UserResponse =            
 Depends(require_auth)):                                                        
     """Clear chat history for current session (legacy)"""                      
     conv_id = request.headers.get("X-Conversation-ID")                         
     if conv_id:                                                                
         # Verify ownership before clearing                                     
         conv = conversation_store.get(conv_id, user_id=user.id)                
         if conv:                                                               
             conversation_store.clear_messages(conv_id)                         
     tool_executor.clear_images()                                               
     return {"status": "cleared"}                                               
                                                                                
 Note: require_auth and UserResponse are already imported in chat.py (used by   
 other endpoints).                                                              
                                                                                
 ---                                                                            
 Verification Steps                                                             
                                                                                
 After implementation, verify each fix:                                         
                                                                                
 # 1. Test CORS - should reject unknown origins                                 
 curl -H "Origin: http://evil.com" -I http://localhost:8080/api/models          
                                                                                
 # 2. Test cookie secure flag (check Set-Cookie header)                         
 curl -v -X POST http://localhost:8080/api/auth/login \                         
   -H "Content-Type: application/json" \                                        
   -d '{"username":"test","password":"test"}'                                   
                                                                                
 # 3. Test JWT warning appears in logs on startup                               
 # Start server and check logs for "SECURITY WARNING: Using default JWT_SECRET" 
                                                                                
 # 4. Test legacy endpoints require auth                                        
 curl http://localhost:8080/api/chat/history  # Should return 401               
 curl -X DELETE http://localhost:8080/api/chat/history  # Should return 401     
                                                                                
 ---                                                                            
 Files Summary                                                                  
 ┌─────────────────────┬──────────────────────────────────────────────┐         
 │        File         │                   Changes                    │         
 ├─────────────────────┼──────────────────────────────────────────────┤         
 │ app/config.py       │ Add CORS_ORIGINS and COOKIE_SECURE variables │         
 ├─────────────────────┼──────────────────────────────────────────────┤         
 │ app/main.py         │ Update CORS middleware, add startup warning  │         
 ├─────────────────────┼──────────────────────────────────────────────┤         
 │ app/routers/auth.py │ Import config, use COOKIE_SECURE in cookies  │         
 ├─────────────────────┼──────────────────────────────────────────────┤         
 │ app/routers/chat.py │ Add require_auth to legacy endpoints         │         
 ├─────────────────────┼──────────────────────────────────────────────┤         
 │ .env.template       │ Document new environment variables           │         
 └─────────────────────┴──────────────────────────────────────────────┘         
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
                                                                                
 Requested permissions:                                                         
   · Bash(prompt: start the application server)                                 
   · Bash(prompt: run curl commands to test endpoints)                          
                                                     
