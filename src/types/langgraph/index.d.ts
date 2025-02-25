declare module "langgraph" {
    export class Graph {
        constructor(config: any);
        query(params: { queryText: string }): Promise<any>;
    }
} 