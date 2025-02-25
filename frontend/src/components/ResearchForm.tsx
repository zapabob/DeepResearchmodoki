import React, { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  CircularProgress,
  Stack,
  FormControlLabel,
  Switch,
  Paper,
  Slider,
} from "@mui/material";
import { ResearchFilters, ResearchFormProps, ResearchTask } from "../types";
import { useNavigate } from "react-router-dom";
import { SelectChangeEvent } from '@mui/material/Select';
import { ResearchRequest } from '../types/research';

type ContentType = "article" | "blog" | "news" | "academic";

export const ResearchForm: React.FC<ResearchFormProps> = ({ onSubmit, loading, disabled }) => {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [maxPages, setMaxPages] = useState(5);
  const [deepSearch, setDeepSearch] = useState(false);
  const [filters, setFilters] = useState<string[]>(['academic', 'news']);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (onSubmit) {
      const request: ResearchRequest = {
        query,
        max_pages: 5,
        language: 'ja',
        depth: deepSearch ? 'deep' : 'shallow',
        filters
      };
      onSubmit(request);
    }
  };

  const handleFilterToggle = (filter: string) => {
    setFilters(prev =>
      prev.includes(filter)
        ? prev.filter(f => f !== filter)
        : [...prev, filter]
    );
  };

  const contentTypes: ContentType[] = ["article", "blog", "news", "academic"];

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
      <form onSubmit={handleSubmit}>
        <Typography variant="h6" gutterBottom>
          深層リサーチ
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="検索クエリ"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading || disabled}
            required
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <TextField
            type="number"
            label="最大ページ数"
            value={maxPages}
            onChange={(e) => setMaxPages(Number(e.target.value))}
            disabled={loading || disabled}
            inputProps={{ min: 1, max: 20 }}
            sx={{ width: 150 }}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={deepSearch}
                onChange={(e) => setDeepSearch(e.target.checked)}
                disabled={loading || disabled}
              />
            }
            label="深層検索を有効にする"
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            フィルター:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {['academic', 'news', 'blog', 'social'].map((filter) => (
              <Chip
                key={filter}
                label={filter}
                onClick={() => handleFilterToggle(filter)}
                color={filters.includes(filter) ? 'primary' : 'default'}
                disabled={loading || disabled}
              />
            ))}
          </Box>
        </Box>

        <Box sx={{ mt: 4, textAlign: "center" }}>
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={loading || !query.trim()}
            sx={{ minWidth: 200 }}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? '検索中...' : '検索開始'}
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default ResearchForm;
