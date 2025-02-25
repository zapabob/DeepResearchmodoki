import { GoogleGenerativeAI } from '@google/generative-ai';

export class GeminiService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor(apiKey: string) {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({ model: "gemini-pro" });
  }

  async analyzeText(text: string): Promise<{
    summary: string;
    sentiment: string;
    keywords: string[];
  }> {
    try {
      const prompt = `
        テキストを分析し、以下の形式でJSONを返してください：
        {
          "summary": "テキストの要約（200文字以内）",
          "sentiment": "感情分析（ポジティブ/ネガティブ/ニュートラル）",
          "keywords": ["重要なキーワード（最大5つ）"]
        }
      `;

      const result = await this.model.generateContent([prompt, text]);
      const response = await result.response;
      const analysisResult = JSON.parse(response.text());

      return {
        summary: analysisResult.summary,
        sentiment: analysisResult.sentiment,
        keywords: analysisResult.keywords
      };
    } catch (error) {
      console.error('GeminiPro analysis failed:', error);
      throw error;
    }
  }

  async generateQuestions(text: string): Promise<string[]> {
    try {
      const prompt = `
        与えられたテキストに関連する重要な質問を3つ生成してください。
        質問は配列形式で返してください。
      `;

      const result = await this.model.generateContent([prompt, text]);
      const response = await result.response;
      return JSON.parse(response.text());
    } catch (error) {
      console.error('Question generation failed:', error);
      throw error;
    }
  }

  async extractEntities(text: string): Promise<{
    name: string;
    type: string;
    relevance: number;
  }[]> {
    try {
      const prompt = `
        テキストから重要なエンティティ（人物、組織、場所、概念など）を抽出し、
        以下の形式でJSONを返してください：
        [
          {
            "name": "エンティティ名",
            "type": "エンティティの種類",
            "relevance": "関連度スコア（0-1）"
          }
        ]
      `;

      const result = await this.model.generateContent([prompt, text]);
      const response = await result.response;
      return JSON.parse(response.text());
    } catch (error) {
      console.error('Entity extraction failed:', error);
      throw error;
    }
  }
}
