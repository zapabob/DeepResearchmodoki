import React, { useState } from 'react';
import { Box, TextField, Button, CircularProgress, FormControlLabel, Checkbox } from '@mui/material';
import { SearchRequest } from '../types/search';

interface SearchFormProps {
  onSubmit: (request: SearchRequest) => Promise<void>;
  loading: boolean;
}

const SearchForm: React.FC<SearchFormProps> = ({ onSubmit, loading }) => {
  const [query, setQuery] = useState('');
  const [hypothesis, setHypothesis] = useState('');
  const [useHypothesis, setUseHypothesis] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const request: SearchRequest = {
      query: query.trim(),
      max_pages: 5,
      hypothesis: useHypothesis ? hypothesis.trim() : undefined,
      use_cot: useHypothesis
    };

    try {
      await onSubmit(request);
    } catch (error) {
      console.error('検索エラー:', error);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mb: 4 }}>
      <TextField
        fullWidth
        label="検索キーワード"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        disabled={loading}
        sx={{ mb: 2 }}
      />
      <FormControlLabel
        control={
          <Checkbox
            checked={useHypothesis}
            onChange={(e) => setUseHypothesis(e.target.checked)}
            disabled={loading}
          />
        }
        label="仮説検証モードを使用"
        sx={{ mb: 2 }}
      />
      {useHypothesis && (
        <TextField
          fullWidth
          label="検証したい仮説"
          value={hypothesis}
          onChange={(e) => setHypothesis(e.target.value)}
          disabled={loading}
          multiline
          rows={3}
          placeholder="例: この検索キーワードに関して、〜という仮説が成り立つと考えられる"
          sx={{ mb: 2 }}
        />
      )}
      <Button
        type="submit"
        variant="contained"
        disabled={loading || !query.trim() || (useHypothesis && !hypothesis.trim())}
        sx={{ minWidth: 120 }}
      >
        {loading ? (
          <>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            {useHypothesis ? '仮説検証中...' : '検索中...'}
          </>
        ) : (
          useHypothesis ? '仮説を検証' : '検索'
        )}
      </Button>
    </Box>
  );
};

export default SearchForm; 