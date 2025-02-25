import React, { useState } from 'react';
import { Box, Typography, Alert, CircularProgress, Card, CardContent, Link, Divider, Chip, Paper } from '@mui/material';
import SearchForm from '../components/SearchForm';
import { searchApi } from '../services/api';
import { SearchResult, SearchResponse } from '../types/search';

const SearchPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);

  const handleSearch = async (request: { query: string; max_pages?: number; hypothesis?: string; use_cot?: boolean }) => {
    console.log('検索リクエストを開始:', request);
    try {
      setLoading(true);
      setError(null);
      const response = await searchApi.search(request);
      console.log('検索が完了しました:', response);
      setSearchResult(response);
    } catch (err) {
      console.error('検索エラー:', err);
      setError(err instanceof Error ? err.message : '検索中にエラーが発生しました');
      setSearchResult(null);
    } finally {
      setLoading(false);
    }
  };

  const renderHypothesisVerification = (verification: SearchResult['hypothesis_verification']) => {
    if (!verification) return null;

    return (
      <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
        <Typography variant="subtitle1" color="primary" gutterBottom>
          仮説検証結果
        </Typography>
        <Typography variant="body1" gutterBottom>
          <strong>結論：</strong> {verification.conclusion}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          <strong>推論過程：</strong> {verification.reasoning}
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip
            label={`信頼度: ${Math.round(verification.confidence * 100)}%`}
            color={verification.confidence > 0.7 ? 'success' : verification.confidence > 0.4 ? 'warning' : 'error'}
            size="small"
            sx={{ mr: 1 }}
          />
        </Box>
        {verification.evidence.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" gutterBottom>
              <strong>根拠：</strong>
            </Typography>
            <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
              {verification.evidence.map((evidence, idx) => (
                <li key={idx}>
                  <Typography variant="body2">{evidence}</Typography>
                </li>
              ))}
            </ul>
          </Box>
        )}
      </Box>
    );
  };

  const renderHypothesisSummary = () => {
    if (!searchResult?.hypothesis_summary) return null;

    const { overall_conclusion, confidence, key_findings, limitations } = searchResult.hypothesis_summary;

    return (
      <Paper sx={{ p: 3, mb: 3, bgcolor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          仮説検証の総合結果
        </Typography>
        <Typography variant="body1" paragraph>
          <strong>総合的な結論：</strong> {overall_conclusion}
        </Typography>
        <Chip
          label={`総合信頼度: ${Math.round(confidence * 100)}%`}
          color={confidence > 0.7 ? 'success' : confidence > 0.4 ? 'warning' : 'error'}
          sx={{ mb: 2 }}
        />
        <Typography variant="subtitle1" gutterBottom>
          主要な発見
        </Typography>
        <ul>
          {key_findings.map((finding, idx) => (
            <li key={idx}>
              <Typography variant="body2">{finding}</Typography>
            </li>
          ))}
        </ul>
        {limitations.length > 0 && (
          <>
            <Typography variant="subtitle1" gutterBottom>
              制限事項・留意点
            </Typography>
            <ul>
              {limitations.map((limitation, idx) => (
                <li key={idx}>
                  <Typography variant="body2" color="text.secondary">
                    {limitation}
                  </Typography>
                </li>
              ))}
            </ul>
          </>
        )}
      </Paper>
    );
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        ウェブ深層検索
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        検索キーワードを入力して、AIによる深層分析を開始してください。
      </Typography>

      <SearchForm onSubmit={handleSearch} loading={loading} />

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {searchResult && (
        <Box sx={{ mt: 4 }}>
          {renderHypothesisSummary()}
          
          <Typography variant="h5" gutterBottom>
            検索結果（{searchResult.results.length}件）
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          {searchResult.results.map((result, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" component="h2" gutterBottom>
                  {result.title}
                </Typography>
                <Link href={result.url} target="_blank" rel="noopener noreferrer" 
                  sx={{ display: 'block', mb: 1, color: 'primary.main' }}>
                  {result.url}
                </Link>
                <Typography variant="body1">
                  {result.snippet}
                </Typography>
                {result.timestamp && (
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    取得日時: {new Date(result.timestamp).toLocaleString('ja-JP')}
                  </Typography>
                )}
                {renderHypothesisVerification(result.hypothesis_verification)}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {searchResult && searchResult.results.length === 0 && (
        <Alert severity="info" sx={{ mt: 2 }}>
          検索結果が見つかりませんでした。別のキーワードで試してみてください。
        </Alert>
      )}
    </Box>
  );
};

export default SearchPage; 