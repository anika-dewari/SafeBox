# 🎬 SafeBox - How to Demonstrate This Project

## ⚡ **FASTEST Demo (5 minutes) - RECOMMENDED**

This is what you should do for your mentor:

### **Step 1: Show Summary (30 sec)**
```bash
cd /Users/gewu/Documents/GitHub/SafeBox
cat FINAL_SUMMARY.txt
```

### **Step 2: Run Complete Demo (3 min)**
```bash
python3 integrated_demo.py complete
```
**Your mentor will see:**
- Multiple processes executing through ALL THREE layers
- [RITIKA] Banker checking → [AYUSH] Monitoring → [ANIKA] Sandbox
- Clear integration with color-coded output

### **Step 3: Show Integration Code (1 min)**
```bash
code integrated_demo.py
```
Go to **line 91** and show how one function calls all three subsystems.

### **Step 4: Verify Real Components (30 sec)**
```bash
./test_real_components.sh
```

**Done! ✅** Your mentor now sees:
- ✅ Integration (all three working together)
- ✅ Real components (not simulated)
- ✅ Team contributions (each visible)

---

## 📊 **Alternative Demos**

### **Option A: Individual Scenarios**

**Normal Flow:**
```bash
python3 integrated_demo.py 1
```
Shows all three working together.

**Deadlock Prevention:**
```bash
python3 integrated_demo.py 2
```
Shows Ritika's Banker rejecting unsafe request.

**Security Enforcement:**
```bash
python3 integrated_demo.py 3
```
Shows Anika's sandbox blocking malicious code.

---

### **Option B: Web Interface**

**Terminal 1 - Backend:**
```bash
cd backend
PYTHONPATH=/Users/gewu/Documents/GitHub/SafeBox/backend \
  python3 -m uvicorn app.main:app --reload --port 8001
```

**Terminal 2 - Web UI:**
```bash
python3 web/app.py
```

**Browser:**
```bash
open http://localhost:5001
```

---

### **Option C: Individual Components**

**Test Banker's Algorithm:**
```bash
python3 demo_banker_algorithm.py
```

**Test Sandbox (needs sudo):**
```bash
make all
sudo ./build/safebox
```

**Test Real System Resources:**
```bash
./test_real_components.sh
```

---

## 🎯 **Complete Demo Flow (15 min)**

If your mentor wants the full walkthrough:

### **1. Introduction (1 min)**
```bash
cat FINAL_SUMMARY.txt
```
Explain: "SafeBox = Docker + Banker's Algorithm"

### **2. Run All Scenarios (10 min)**
```bash
python3 integrated_demo.py
```
This runs all scenarios with pauses between each.

### **3. Show Code (2 min)**
```bash
code integrated_demo.py
```
Navigate to line 91-204 and explain integration.

### **4. Verify Real Components (2 min)**
```bash
./test_real_components.sh
```

---

## 🎤 **Presentation Script**

### **Opening:**
> "Let me show you SafeBox - our integrated secure execution system. Watch how all three team members' work connects together."

### **Run:**
```bash
python3 integrated_demo.py complete
```

### **Narrate:**
> "See how every process goes through:
> 1. RITIKA's Banker (deadlock prevention)
> 2. AYUSH's cgroups (resource monitoring)  
> 3. ANIKA's sandbox (security isolation)
> This is ONE integrated system."

### **Show Code:**
```bash
code integrated_demo.py  # Line 91
```
> "Here's the integration. One function orchestrates all three. Each phase uses data from the previous phase."

### **Closing:**
> "The core components are real Linux kernel features. The demo simulates execution for clarity, but I can show you the actual components."

---

## 💻 **All Available Commands**

### **Main Demos:**
```bash
python3 integrated_demo.py complete    # Complete workflow
python3 integrated_demo.py            # All scenarios (interactive)
python3 integrated_demo.py 1          # Scenario 1: Normal
python3 integrated_demo.py 2          # Scenario 2: Deadlock
python3 integrated_demo.py 3          # Scenario 3: Security
python3 integrated_demo.py 4          # Scenario 4: Multiple processes
```

### **Component Tests:**
```bash
python3 demo_banker_algorithm.py      # Banker's Algorithm
sudo ./build/safebox                  # Sandbox (needs build)
./test_real_components.sh             # Verify real components
```

### **Build & Run:**
```bash
make all                              # Build C/C++ components
make integrated-demo                  # Run integrated demo
make demo-all                         # All scenarios
make start-integrated                 # Start backend + web
```

### **Documentation:**
```bash
cat FINAL_SUMMARY.txt                 # Quick summary
cat WHAT_THIS_PROJECT_DOES.md         # Full explanation
cat INTEGRATION_SUMMARY.md            # Integration details
open MENTOR_PRESENTATION_GUIDE.md     # Presentation guide
```

---

## 🔧 **Troubleshooting**

### **If demo fails:**
```bash
# Install dependencies
pip3 install -r backend/requirements.txt

# Try again
python3 integrated_demo.py complete
```

### **If import errors:**
```bash
# Check you're in the right directory
pwd
# Should be: /Users/gewu/Documents/GitHub/SafeBox

cd /Users/gewu/Documents/GitHub/SafeBox
```

### **If web UI port conflict:**
```bash
# Kill existing process
lsof -i :5001
kill -9 <PID>

# Or use different port (already configured)
python3 web/app.py  # Uses port 5001
```

---

## ✅ **Pre-Demo Checklist**

Before presenting:

- [ ] In correct directory: `/Users/gewu/Documents/GitHub/SafeBox`
- [ ] Dependencies installed: `pip3 list | grep fastapi`
- [ ] Demo works: `python3 integrated_demo.py 1`
- [ ] Test script works: `./test_real_components.sh`
- [ ] Know integration code location: Line 91 in `integrated_demo.py`
- [ ] Terminal is clean
- [ ] Can explain what's real vs simulated

---

## 💡 **Pro Tips**

1. **Start with the 5-minute demo**
   - If mentor wants more → show individual scenarios
   - If mentor wants code → show integration function

2. **Use the color coding**
   - Point out [RITIKA], [AYUSH], [ANIKA] labels
   - Shows visual team contributions

3. **Emphasize sequential flow**
   - "Notice AYUSH only runs if RITIKA approves"
   - "See how ANIKA uses AYUSH's cgroup path"

4. **Be honest about simulation**
   - "Demo simulates for presentation clarity"
   - "But all components are real - let me show you"

5. **Have the verification ready**
   - `./test_real_components.sh` proves it's real
   - Shows actual system resources detected

---

## 🎓 **Expected Questions**

### **"Is this three separate projects?"**
**Show:** Scenario 2 where Ritika rejects and others don't run.
**Say:** "That's real integration - one component controls the others."

### **"Are these real OS components?"**
**Show:** `./test_real_components.sh`
**Say:** "Yes, we use actual Linux kernel APIs - same as Docker."

### **"What's simulated?"**
**Say:** "Only the demo wrapper. The core components (namespaces, cgroups, seccomp, Banker) are 100% real. I can show you."

---

## 🚀 **RECOMMENDED APPROACH**

**For your mentor, do this:**

```bash
# 1. Quick intro
cat FINAL_SUMMARY.txt | head -40

# 2. Run complete demo
python3 integrated_demo.py complete

# 3. Show integration code
code integrated_demo.py  # Go to line 91

# 4. Verify it's real
./test_real_components.sh
```

**Total: ~7 minutes**

**This shows:**
- ✅ All three integrated
- ✅ Real OS components
- ✅ Team contributions visible
- ✅ Professional implementation

---

## 📚 **Documentation to Reference**

During demo, have these open:

1. **FINAL_SUMMARY.txt** - Quick reference
2. **MENTOR_PRESENTATION_GUIDE.md** - Full script
3. **integrated_demo.py** - The actual code
4. **WHAT_THIS_PROJECT_DOES.md** - Detailed explanation

---

**You're ready to demonstrate! Good luck! 🚀💪**
