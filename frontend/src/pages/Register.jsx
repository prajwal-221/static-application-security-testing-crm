import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Button } from 'antd';
import useLanguage from '@/locale/useLanguage';
import { register } from '@/redux/auth/actions';
import { selectAuth } from '@/redux/auth/selectors';
import RegisterForm from '@/forms/RegisterForm';
import Loading from '@/components/Loading';
import AuthModule from '@/modules/AuthModule';

const RegisterPage = () => {
    const translate = useLanguage();
    const { isLoading, isSuccess } = useSelector(selectAuth);
    const navigate = useNavigate();
    const dispatch = useDispatch();

    const onFinish = (values) => {
        dispatch(register({ registerData: values }));
    };

    useEffect(() => {
        if (isSuccess) navigate('/login');
    }, [isSuccess]);

    const FormContainer = () => {
        return (
            <Loading isLoading={isLoading}>
                <Form layout="vertical" name="normal_register" className="login-form" onFinish={onFinish}>
                    <RegisterForm />
                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            className="login-form-button"
                            loading={isLoading}
                            size="large"
                        >
                            {translate('Register')}
                        </Button>
                        {translate('Or')}{' '}
                        <Link to="/login">
                            {translate('already have an account? Login now')}
                        </Link>
                    </Form.Item>
                </Form>
            </Loading>
        );
    };

    return <AuthModule authContent={<FormContainer />} AUTH_TITLE="Sign up" isForRegistre={true} />;
};

export default RegisterPage;
