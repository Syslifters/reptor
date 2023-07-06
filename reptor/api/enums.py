from enum import StrEnum


class OWASP_TOP10_2021(StrEnum):
    A01_2021: str = "A01_2021"  #'A01:2021 - Broken Access Control'
    A02_2021: str = "A02_2021"  #'A02:2021 - Cryptographic Failures'
    A03_2021: str = "A03_2021"  #'A03:2021 - Injection'
    A04_2021: str = "A04_2021"  #'A04:2021 - Insecure Design'
    A05_2021: str = "A05_2021"  #'A05:2021 - Security Misconfiguration'
    A06_2021: str = "A06_2021"  #'A06:2021 - Vulnerable and Outdated Components'
    A07_2021: str = "A07_2021"  #'A07:2021 - Identification and Authentication Failures'
    A08_2021: str = "A08_2021"  #'A08:2021 - Software and Data Integrity Failures'
    A09_2021: str = "A09_2021"  #'A09:2021 - Security Logging and Monitoring Failures'
    A10_2021: str = "A10_2021"  #'A10:2021 - Server-Side Request Forgery (SSRF)'


class WSTG_CATEGORY(StrEnum):
    INFO: str = "INFO"  # Information Gathering
    CONF: str = "CONF"  # Configuration and Deployment Management
    IDNT: str = "IDNT"  # Identity Management
    ATHN: str = "ATHN"  # Authentication
    ATHZ: str = "ATHZ"  # Authorization
    SESS: str = "SESS"  # Session Management
    INPV: str = "INPV"  # Input Validation
    ERRH: str = "ERRH"  # Error Handling
    CRYP: str = "CRYP"  # Weak Cryptography
    BUSL: str = "BUSL"  # Business Logic
    CLNT: str = "CLNT"  # Client-side Testing
    APIT: str = "APIT"  # API Testing


class RETEST_STATUS(StrEnum):
    OPEN: str = "open"
    RESOLVED: str = "resolved"
    PARTIALLY_RESOLVED: str = "partial"
    CHANGED: str = "changed"
    ACCEPTED: str = "accepted"
    NEW: str = "new"
