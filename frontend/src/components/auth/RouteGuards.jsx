import { Navigate, Outlet } from 'react-router-dom';
import useAuthStore from '../../stores/authStore';

/** Only renders children if user is authenticated */
export function ProtectedRoute() {
    const { isAuthenticated, isLoading } = useAuthStore();
    if (isLoading) return null;
    return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

/** Only renders children if user is NOT authenticated */
export function GuestRoute() {
    const { isAuthenticated, isLoading } = useAuthStore();
    if (isLoading) return null;
    return !isAuthenticated ? <Outlet /> : <Navigate to="/" replace />;
}
