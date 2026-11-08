# התקנה על Windows

כל הפקודות ב-**Command Prompt** (מחפשים `cmd` בתפריט התחל), לא PowerShell: במחשבים רבים מדיניות ההרצה של PowerShell חוסמת את `npm` ואת `npx`. לא צריך מנהל מערכת. אחרי כל התקנה סוגרים ופותחים את החלון מחדש.

## 1. הבסיס
```
winget install --id Git.Git -e          # Git + Git Bash (ההוקים והכלי Bash של קלוד משתמשים בו)
winget install --id OpenJS.NodeJS.LTS -e # Node: ל-Remotion, HyperFrames ושרתי MCP
winget install --id Python.Python.3.12 -e # Python: להוקים ולגשר הטלגרם
winget install --id Gyan.FFmpeg -e       # FFmpeg: לרינדור וידאו
```
בדיקה: `git --version && node --version && python --version && ffmpeg -version`

## 2. Claude Code (אם עוד לא מותקן)
```
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```
נוצר `%USERPROFILE%\.local\bin\claude.exe`. בדיקה: `claude --version`.
⛔ גשר הטלגרם דורש את ההתקנה הזאת (claude.exe), לא התקנה דרך npm.

## 3. Remotion (וידאו מקוד React)
```
cd %USERPROFILE%\Documents
npx create-video@latest
```
בוחרים תבנית, נכנסים לתיקייה, `npm run dev` פותח את הסטודיו בדפדפן.

## 4. HyperFrames (וידאו מ-HTML)
```
npx hyperframes skills            # מתקין לקלוד את הסקילים של HyperFrames
npx hyperframes init my-video     # פרויקט ראשון
cd my-video && npx hyperframes preview
```
עדכון סקילים בהמשך: `npx hyperframes skills update` (נבדק בגרסה 0.9.23, 08.11.2026).

## 5. ההגדרות של הקיט
```
mkdir %USERPROFILE%\.claude\hooks %USERPROFILE%\.claude\agents
copy claude-config\hooks\*.py %USERPROFILE%\.claude\hooks\
copy claude-config\agents\*.md %USERPROFILE%\.claude\agents\
```
- `settings.example.json`: ממזגים לתוך `%USERPROFILE%\.claude\settings.json` (לא דורסים קובץ קיים).
- `CLAUDE.template.md`: ממלאים ושומרים כ-`%USERPROFILE%\.claude\CLAUDE.md`.
- בדיקה: בתוך קלוד מבקשים "תריץ rm -rf test". ההוק צריך לחסום.
