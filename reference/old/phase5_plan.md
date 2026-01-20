Phase 5: Configuration & Deployment Fixes                                                                                                                        
                                                                                                                                                                  
 Summary                                                                                                                                                          
                                                                                                                                                                  
 Fix 4 configuration and deployment issues in PeanutChat: tool filtering, deprecated datetime, service file improvements, and shell script error handling.        
                                                                                                                                                                  
 ---                                                                                                                                                              
 Task 5.1: Update get_tools_for_model() to Filter by Capabilities                                                                                                 
                                                                                                                                                                  
 Files:                                                                                                                                                           
 - app/tools/definitions.py (modify function)                                                                                                                     
 - app/routers/chat.py (update 2 call sites)                                                                                                                      
                                                                                                                                                                  
 Changes to app/tools/definitions.py (lines 76-78):                                                                                                               
                                                                                                                                                                  
 Replace:                                                                                                                                                         
 def get_tools_for_model():                                                                                                                                       
     """Get available tools for tool-capable models"""                                                                                                            
     return ALL_TOOLS                                                                                                                                             
                                                                                                                                                                  
 With:                                                                                                                                                            
 def get_tools_for_model(supports_tools: bool = True, supports_vision: bool = False) -> list:                                                                     
     """Get available tools filtered by model capabilities"""                                                                                                     
     if not supports_tools:                                                                                                                                       
         return []                                                                                                                                                
                                                                                                                                                                  
     tools = ALL_TOOLS.copy()                                                                                                                                     
                                                                                                                                                                  
     # Filter vision-only tools if model doesn't support vision                                                                                                   
     if not supports_vision:                                                                                                                                      
         tools = [t for t in tools if t.get('function', {}).get('name') != 'analyze_image']                                                                       
                                                                                                                                                                  
     return tools                                                                                                                                                 
                                                                                                                                                                  
 Changes to app/routers/chat.py:                                                                                                                                  
                                                                                                                                                                  
 Line 155 - change:                                                                                                                                               
 tools = get_tools_for_model() if supports_tools else None                                                                                                        
 To:                                                                                                                                                              
 tools = get_tools_for_model(supports_tools=supports_tools, supports_vision=is_vision)                                                                            
                                                                                                                                                                  
 Line 605 - same change:                                                                                                                                          
 tools = get_tools_for_model(supports_tools=supports_tools, supports_vision=is_vision)                                                                            
                                                                                                                                                                  
 ---                                                                                                                                                              
 Task 5.2: Fix Deprecated datetime.utcnow()                                                                                                                       
                                                                                                                                                                  
 File: app/services/auth_service.py                                                                                                                               
                                                                                                                                                                  
 Line 76 - change:                                                                                                                                                
 created_at = datetime.utcnow().isoformat()                                                                                                                       
 To:                                                                                                                                                              
 created_at = datetime.now(timezone.utc).isoformat()                                                                                                              
                                                                                                                                                                  
 Note: timezone is already imported on line 2.                                                                                                                    
                                                                                                                                                                  
 ---                                                                                                                                                              
 Task 5.3: Improve Systemd Service File                                                                                                                           
                                                                                                                                                                  
 File: peanutchat.service                                                                                                                                         
                                                                                                                                                                  
 Replace entire contents with:                                                                                                                                    
 [Unit]                                                                                                                                                           
 Description=PeanutChat AI Assistant                                                                                                                              
 After=network.target ollama.service                                                                                                                              
 Wants=ollama.service                                                                                                                                             
                                                                                                                                                                  
 [Service]                                                                                                                                                        
 Type=simple                                                                                                                                                      
 User=tech                                                                                                                                                        
 Group=tech                                                                                                                                                       
 WorkingDirectory=/home/tech/PeanutChat                                                                                                                           
 ExecStart=/home/tech/PeanutChat/venv/bin/python3 /home/tech/PeanutChat/run.py                                                                                    
 Restart=always                                                                                                                                                   
 RestartSec=5                                                                                                                                                     
                                                                                                                                                                  
 # Logging - capture stdout/stderr to journald                                                                                                                    
 StandardOutput=journal                                                                                                                                           
 StandardError=journal                                                                                                                                            
 SyslogIdentifier=peanutchat                                                                                                                                      
                                                                                                                                                                  
 # Environment                                                                                                                                                    
 Environment=PYTHONUNBUFFERED=1                                                                                                                                   
 Environment="PATH=/home/tech/PeanutChat/venv/bin:/usr/local/bin:/usr/bin:/bin"                                                                                   
                                                                                                                                                                  
 [Install]                                                                                                                                                        
 WantedBy=multi-user.target                                                                                                                                       
                                                                                                                                                                  
 Changes:                                                                                                                                                         
 - Added ollama.service dependency (After/Wants)                                                                                                                  
 - Added PATH environment variable for reliable execution                                                                                                         
                                                                                                                                                                  
 ---                                                                                                                                                              
 Task 5.4: Add Shell Script Error Handling                                                                                                                        
                                                                                                                                                                  
 File: start_peanutchat.sh                                                                                                                                        
                                                                                                                                                                  
 Replace entire contents with:                                                                                                                                    
 #!/bin/bash                                                                                                                                                      
 set -euo pipefail                                                                                                                                                
                                                                                                                                                                  
 SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"                                                                                                       
 cd "$SCRIPT_DIR"                                                                                                                                                 
                                                                                                                                                                  
 if [ ! -d "venv" ]; then                                                                                                                                         
     echo "Error: Virtual environment not found at $SCRIPT_DIR/venv"                                                                                              
     echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"                                                              
     exit 1                                                                                                                                                       
 fi                                                                                                                                                               
                                                                                                                                                                  
 echo "Starting PeanutChat from $SCRIPT_DIR..."                                                                                                                   
 source venv/bin/activate                                                                                                                                         
 exec python3 run.py                                                                                                                                              
                                                                                                                                                                  
 Changes:                                                                                                                                                         
 - Added set -euo pipefail for strict error handling                                                                                                              
 - Script directory auto-detection (portable)                                                                                                                     
 - Virtual environment validation with helpful error message                                                                                                      
 - Using exec to replace shell process                                                                                                                            
                                                                                                                                                                  
 ---                                                                                                                                                              
 Verification                                                                                                                                                     
                                                                                                                                                                  
 # 1. Test Python syntax                                                                                                                                          
 python3 -m py_compile app/tools/definitions.py                                                                                                                   
 python3 -m py_compile app/services/auth_service.py                                                                                                               
 python3 -m py_compile app/routers/chat.py                                                                                                                        
                                                                                                                                                                  
 # 2. Test shell script (should fail gracefully if venv missing)                                                                                                  
 bash -n start_peanutchat.sh  # syntax check                                                                                                                      
                                                                                                                                                                  
 # 3. Validate service file syntax                                                                                                                                
 systemd-analyze verify peanutchat.service 2>&1 || true                                                                                                           
                                                                                                                                                                  
 # 4. Start the application and test chat endpoint                                                                                                                
 ./start_peanutchat.sh &                                                                                                                                          
 sleep 3                                                                                                                                                          
 curl -s http://localhost:8000/api/health | head -1                                                                                                               
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
                                                                                                                                                                  
 Requested permissions:                                                                                                                                           
   · Bash(prompt: run Python syntax check)                                                                                                                        
   · Bash(prompt: run shell script syntax check)                                                                                                                  
   · Bash(prompt: validate systemd service file)                                                                                                                  
   · Bash(prompt: start application for testing)                                                                                                                  
   · Bash(prompt: test health endpoint)     
