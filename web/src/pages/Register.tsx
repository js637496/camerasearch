import React, { useState } from 'react'
import { useRegisterMutation } from '../generated/graphql';
import { RouteComponentProps } from 'react-router-dom';

interface Props {

}

export const Register: React.FC<RouteComponentProps> = ({history}) => {

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [security, setSecurity] = useState('');
    const [register] = useRegisterMutation();

    return (
        <form 
            onSubmit={async e => {
                e.preventDefault()
                console.log('form submitted');
                const response = await register({
                    variables: {
                        email,
                        password
                    }
                })

                console.log(response);
                history.push('/');                
            }}
        >
            <div>
                <input 
                    value={email}
                    placeholder="email"
                    onChange={e => {
                        setEmail(e.target.value);
                    }}
                />
            </div>
            <div>
                <input 
                    type="password"
                    value={password}
                    placeholder="password"
                    onChange={e => {
                        setPassword(e.target.value);
                    }}
                />
            </div>
            <div>
                <input 
                    value={security}
                    placeholder="0"
                    onChange={e => {
                        setSecurity(e.target.value);
                    }}
                />
            </div>
            <button type="submit">register</button>
        </form>
    );
}