import React, { useState } from 'react';
import { Box, Container, TextField, Button, Typography, Paper, CircularProgress, Divider } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { ForceGraph2D } from 'react-force-graph';
import { GraphService } from '../services/GraphService';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
});

const config = {
  graph: {
    uri: process.env.REACT_APP_NEO4J_URI || 'bolt://localhost:7687',
    username: process.env.REACT_APP_NEO4J_USER || 'neo4j',
    password: process.env.REACT_APP_NEO4J_PASSWORD || 'password'
  }
};

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [graphData, setGraphData] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const graphService = new GraphService(
    config.graph.uri,
    config.graph.username,
    config.graph.password
  );

  const handleResearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // 検索リクエストの送信
      const response = await fetch('/api/deepresearch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('検索リクエストが失敗しました');
      }

      const crawlResults = await response.json();
      
      // 検索結果の処理
      const searchResults = crawlResults.slice(0, -1); // 最後の要素（分析）を除外
      const analysis = crawlResults[crawlResults.length - 1]; // 最後の要素（分析）

      // グラフデータの生成
      const graphData = await graphService.createGraph(analysis);
      setGraphData(graphData);

      // 検索結果の設定
      setResults(searchResults);

      // サマリーの設定
      setSummary({
        title: analysis.title,
        content: analysis.content,
        metadata: analysis.metadata,
        deepWebSummary: analysis.metadata.deepWebSummary,
        sentiment: analysis.metadata.sentiment,
        insights: analysis.metadata.insights,
        keywords: analysis.metadata.keywords,
        stats: {
          totalPages: analysis.metadata.metadata.totalPages,
          processedEntities: analysis.metadata.metadata.processedEntities,
          deepWebSources: analysis.metadata.metadata.deepWebSources,
          processingTime: analysis.metadata.metadata.processingTime
        }
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Web Deep Research
          </Typography>

          <form onSubmit={handleResearchSubmit}>
            <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
              <TextField
                fullWidth
                label="検索クエリ"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
              />
              <Button
                type="submit"
                variant="contained"
                disabled={loading || !query.trim()}
              >
                検索
              </Button>
            </Box>
          </form>

          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {error && (
            <Paper sx={{ p: 2, mb: 4, bgcolor: 'error.dark' }}>
              <Typography color="error">{error}</Typography>
            </Paper>
          )}

          {summary && (
            <Paper sx={{ p: 3, mb: 4 }}>
              <Typography variant="h5" gutterBottom>
                分析結果
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6">全体要約</Typography>
                <Typography>{summary.deepWebSummary}</Typography>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6">感情分析</Typography>
                <Typography>{summary.sentiment}</Typography>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6">主要な洞察</Typography>
                <ul>
                  {summary.insights.map((insight: string, index: number) => (
                    <li key={index}>
                      <Typography>{insight}</Typography>
                    </li>
                  ))}
                </ul>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6">キーワード</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {summary.keywords.map((keyword: string, index: number) => (
                    <Paper key={index} sx={{ p: 1 }}>
                      <Typography variant="body2">{keyword}</Typography>
                    </Paper>
                  ))}
                </Box>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box>
                <Typography variant="h6">統計情報</Typography>
                <Typography>
                  総ページ数: {summary.stats.totalPages} |
                  処理エンティティ数: {summary.stats.processedEntities} |
                  深層Webソース: {summary.stats.deepWebSources} |
                  処理時間: {summary.stats.processingTime.toFixed(2)}秒
                </Typography>
              </Box>
            </Paper>
          )}

          {graphData && (
            <Paper sx={{ p: 3, mb: 4, height: '500px' }}>
              <Typography variant="h5" gutterBottom>
                知識グラフ
              </Typography>
              <ForceGraph2D
                graphData={graphData}
                nodeLabel="label"
                nodeAutoColorBy="type"
                linkDirectionalParticles={2}
              />
            </Paper>
          )}

          {results.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                検索結果
              </Typography>
              {results.map((result, index) => (
                <Paper key={index} sx={{ p: 2, mb: 2 }}>
                  <Typography variant="h6" component="a" href={result.url} target="_blank">
                    {result.title}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    {result.url}
                  </Typography>
                  <Typography>{result.metadata.summary}</Typography>
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption">
                      ソース: {result.metadata.source} |
                      ランク: {result.metadata.rank} |
                      スコア: {result.metadata.score}
                    </Typography>
                  </Box>
                </Paper>
              ))}
            </Paper>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
