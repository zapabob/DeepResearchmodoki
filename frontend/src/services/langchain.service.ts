export class LangChain {
  private steps: Map<string, Function> = new Map();

  addStep(name: string, fn: Function) {
    this.steps.set(name, fn);
    return this;
  }

  async execute(input: any) {
    let result = input;
    for (const [_, fn] of this.steps) {
      result = await fn(result);
    }
    return result;
  }
} 