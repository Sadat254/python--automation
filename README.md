 🐍 Python IT Automation Scripts

> A collection of Python scripts built to automate common IT administration tasks — reducing manual effort and improving efficiency for systems and network administrators.

---

 📦 Scripts Included

 1. 🔍 Network Ping Scanner (`network_scanner.py`)
Scans a network range concurrently and reports which devices are online, with hostname resolution and optional report export.

Features:
- Concurrent scanning using ThreadPoolExecutor (fast)
- Hostname resolution for online devices
- Configurable network range (e.g. `192.168.1.0/24`)
- Save results to a timestamped report file
- Progress tracking during scan

Usage:
```bash
 Basic scan
python network_scanner.py --range 192.168.1.0/24

 Save results to file
python network_scanner.py --range 192.168.1.0/24 --save

 Adjust thread count for speed
python network_scanner.py --range 10.0.0.0/24 --workers 100
```

---

 2. 💾 Auto Backup Tool (`auto_backup.py`)
Backs up files from a source folder to a destination with timestamped versioning, incremental change detection (MD5 hash), and detailed logging.

Features:
- Incremental backup — only copies changed files
- MD5 hash comparison to detect file changes
- Timestamped backup folders (`backup_20241015_143022/`)
- Detailed logs saved to file + printed to console
- Full backup option available

Usage:
```bash
 Incremental backup (default)
python auto_backup.py --src /path/to/source --dest /path/to/backup

 Full backup (copy everything)
python auto_backup.py --src /path/to/source --dest /path/to/backup --full
```

---

 ⚙️ Requirements

No external libraries needed — both scripts use Python's standard library only.

- Python 3.8+

---

 🚀 Getting Started

```bash
git clone https://github.com/Sadat254/python-automation.git
cd python-automation
python network_scanner.py --range 192.168.1.0/24
```

---

 👤 Author

Alvine Sadat  
📧 sadatalvine@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/alvine-sadat-909b4b215) | [GitHub](https://github.com/Sadat254)

