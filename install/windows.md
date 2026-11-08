# התקנה על Windows

כל הפקודות ב-PowerShell רגיל (לא צריך מנהל מערכת). אחרי כל התקנה סוגרים ופותחים את PowerShell מחדש.

## 1. הבסיס
```powershell
winget install --id Git.Git -e          # Git + Git Bash (ההוקים והכלי Bash של קלוד משתמשים בו)
winget install --id OpenJS.NodeJS.LTS -e # Node: ל-Remotion, HyperFrames ושרתי MCP
winget install --id Python.Python.3.12 -e # Python: להוקים ולגשר הטלגרם
winget install --id Gyan.FFmpeg -e       # FFmpeg: לרינדור וידאו
```
בדיקה: `git --version; node --version; python --version; ffmpeg -version`

## 2. Claude Code (אם עוד לא מותקן)
```powershell
irm https://claude.ai/install.ps1 | iex
```
נוצר `%USERPROFILE%\.local\bin\claude.exe`. בדיקה: `claude --version`.
⛔ גשר הטלגרם דורש את ההתקנה הזאת (claude.exe), לא התקנה דרך npm.

## 3. Remotion (וידאו מקוד React)
```powershell
cd $HOME\Documents
npx create-video@latest
```
בוחרים תבנית, נכנסים לתיקייה, `npm run dev` פותח את הסטודיו בדפדפן.

## 4. HyperFrames (וידאו מ-HTML)
```powershell
npx hyperframes skills            # מתקין לקלוד את הסקילים של HyperFrames
npx hyperframes init my-video     # פרויקט ראשון
cd my-video; npx hyperframes preview
```
עדכון סקילים בהמשך: `npx hyperframes skills update` (נבדק בגרסה 0.9.23, 08.11.2026).

## 5. ההגדרות של הקיט
```powershell
mkdir $HOME\.claude\hooks -Force
copy claude-config\hooks\*.py $HOME\.claude\hooks\
copy claude-config\agents\*.md $HOME\.claude\agents\
```
- `settings.example.json`: ממזגים לתוך `%USERPROFILE%\.claude\settings.json` (לא דורסים קובץ קיים).
- `CLAUDE.template.md`: ממלאים ושומרים כ-`%USERPROFILE%\.claude\CLAUDE.md`.
- בדיקה: בתוך קלוד מבקשים "תריץ rm -rf test". ההוק צריך לחסום.
