/**
 * Universal Frontend Test Runner for SIH26034
 * Runs compliance.test.js in Node.js, Headless Browser, or Interactive HTML page.
 */

import { runTests } from "./compliance.test.js";

class TestRunner {
  constructor() {
    this.passed = 0;
    this.failed = 0;
    this.total = 0;
    this.logs = [];
  }

  async test(name, fn) {
    this.total++;
    try {
      await fn();
      this.passed++;
      this.log(`✓ PASS: ${name}`, "pass");
    } catch (err) {
      this.failed++;
      this.log(`✗ FAIL: ${name}\n  ${err.message}`, "fail");
    }
  }

  ok(condition, message = "Condition failed") {
    if (!condition) throw new Error(message);
  }

  equal(actual, expected, message = "") {
    if (actual !== expected) {
      throw new Error(`${message || "Values not equal"}: expected '${expected}', got '${actual}'`);
    }
  }

  log(msg, type = "info") {
    this.logs.push({ msg, type });
    if (typeof console !== "undefined") {
      if (type === "pass") console.log("\x1b[32m" + msg + "\x1b[0m");
      else if (type === "fail") console.error("\x1b[31m" + msg + "\x1b[0m");
      else console.log(msg);
    }
  }

  summary() {
    const summaryText = `\n========================================\nTEST SUITE SUMMARY:\nTotal: ${this.total} | Passed: ${this.passed} | Failed: ${this.failed}\n========================================\n`;
    if (this.failed === 0) {
      console.log("\x1b[32m\x1b[1m" + summaryText + "\x1b[0m");
    } else {
      console.error("\x1b[31m\x1b[1m" + summaryText + "\x1b[0m");
    }
    return {
      passed: this.passed,
      failed: this.failed,
      total: this.total,
      success: this.failed === 0,
    };
  }
}

export async function executeTestSuite() {
  const runner = new TestRunner();
  console.log("Starting SIH26034 P4 Frontend Compliance Test Suite...\n");
  await runTests(runner);
  return runner.summary();
}

// Auto-run if executed in Node environment
if (typeof process !== "undefined" && process.argv && process.argv[1]?.endsWith("runner.js")) {
  executeTestSuite().then((res) => {
    if (!res.success) process.exit(1);
  });
}
