import { execSync } from "node:child_process";

export default function ({ tool }) {
  // Хук OpenCode 2: перехват события после выполнения файловых операций
  tool.hook("execute.after", async ({ toolName, result }) => {
    if (toolName === "edit" || toolName === "write") {
      try {
        const out = execSync("sh scripts/check.sh", { encoding: "utf-8" });
        return {
          ...result,
          hookOutput: `\n[AUTOMATED HOOK PASS]\n${out}`
        };
      } catch (err) {
        return {
          ...result,
          hookOutput: `\n[AUTOMATED HOOK FAIL]\n${err.stdout || err.message}`
        };
      }
    }
  });
}
