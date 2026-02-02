import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import UploadPage from '../pages/upload/index';
import * as billing from '../hooks/useBilling';
import * as teamSettings from '../hooks/useTeamSettings';

// Mock hooks
vi.mock('../hooks/useBilling', () => ({
  useUsage: vi.fn(),
  usePricing: vi.fn(),
}));

vi.mock('../hooks/useTeamSettings', () => ({
  useTeamSettings: vi.fn(),
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('UploadPage', () => {
  beforeEach(() => {
    vi.mocked(billing.useUsage).mockReturnValue({
      data: {
        monthly_upload_count: 5,
        monthly_limit: 10,
        extra_credits: 0,
        plan: 'STANDARD',
      },
      isLoading: false,
    } as any);
    vi.mocked(billing.usePricing).mockReturnValue({
      data: {
        plans: [{ plan: 'STANDARD', limits: { members: 10, languages: 5 } }],
      },
      isLoading: false,
    } as any);
    vi.mocked(teamSettings.useTeamSettings).mockReturnValue({
      data: { members_count: 3 },
      isLoading: false,
    } as any);
  });

  it('renders upload page with title', () => {
    renderWithRouter(<UploadPage />);
    expect(screen.getByText('Upload Audio')).toBeInTheDocument();
  });

  it('renders file and URL tabs', () => {
    renderWithRouter(<UploadPage />);
    expect(screen.getByRole('tab', { name: /upload file/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /from url/i })).toBeInTheDocument();
  });

  it('validates YouTube URLs correctly', async () => {
    const user = userEvent.setup();
    renderWithRouter(<UploadPage />);

    const urlTab = screen.getByRole('tab', { name: /from url/i });
    await user.click(urlTab);

    const urlInput = screen.getByPlaceholderText(/youtube\.com/i);
    await user.type(urlInput, 'https://youtube.com/watch?v=abc123');

    expect(screen.queryByText(/invalid url/i)).not.toBeInTheDocument();
  });

  it('shows error for invalid URLs', async () => {
    const user = userEvent.setup();
    renderWithRouter(<UploadPage />);

    const urlTab = screen.getByRole('tab', { name: /from url/i });
    await user.click(urlTab);

    const urlInput = screen.getByPlaceholderText(/youtube\.com/i);
    await user.type(urlInput, 'not-a-url');

    expect(screen.getByText(/invalid url/i)).toBeInTheDocument();
  });

  it('shows PlanLimitCard when limit reached', () => {
    vi.mocked(billing.useUsage).mockReturnValue({
      data: {
        monthly_upload_count: 10,
        monthly_limit: 10,
        extra_credits: 0,
        plan: 'STANDARD',
      },
      isLoading: false,
    } as any);
    vi.mocked(billing.usePricing).mockReturnValue({
      data: { plans: [{ plan: 'STANDARD', limits: { members: 10, languages: 5 } }] },
      isLoading: false,
    } as any);

    renderWithRouter(<UploadPage />);
    expect(screen.getByText(/upload limit reached/i)).toBeInTheDocument();
  });

  it('disables upload when limit reached', () => {
    vi.mocked(billing.useUsage).mockReturnValue({
      data: {
        monthly_upload_count: 10,
        monthly_limit: 10,
        extra_credits: 0,
        plan: 'STANDARD',
      },
      isLoading: false,
    } as any);
    vi.mocked(billing.usePricing).mockReturnValue({
      data: { plans: [{ plan: 'STANDARD', limits: { members: 10, languages: 5 } }] },
      isLoading: false,
    } as any);

    renderWithRouter(<UploadPage />);
    const uploadCard = screen.getByText(/transcribe audio/i).closest('.opacity-50');
    expect(uploadCard).toBeInTheDocument();
  });

  it('shows TeamLimitCard when member limit reached', () => {
    vi.mocked(teamSettings.useTeamSettings).mockReturnValue({
      data: { members_count: 10 },
      isLoading: false,
    } as any);
    vi.mocked(billing.usePricing).mockReturnValue({
      data: { plans: [{ plan: 'FREE', limits: { members: 5, languages: 1 } }] },
      isLoading: false,
    } as any);
    vi.mocked(billing.useUsage).mockReturnValue({
      data: {
        plan: 'FREE',
        monthly_upload_count: 5,
        monthly_limit: 10,
        extra_credits: 0,
      },
      isLoading: false,
    } as any);

    renderWithRouter(<UploadPage />);
    expect(screen.getByText(/team member limit reached/i)).toBeInTheDocument();
  });
});
