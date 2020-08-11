import React from 'react'
import { Link } from 'react-router-dom';
import { useMeQuery, useLogoutMutation } from './generated/graphql';
import { setAccessToken } from './accessToken';
import { Navbar, NavDropdown, Nav } from 'react-bootstrap';
import { LinkContainer} from 'react-router-bootstrap';


interface Props {

}

export const Header: React.FC<Props> = ({}) => {

    const { data, loading } = useMeQuery();
    const [logout, {client}] = useLogoutMutation();

    let body: any = null;

    if (loading) {
        body = null;    
    } else if (data && data.me) {
        body = <div>you are logged in as {data.me.email}</div>;
    } else {
        body = <div>not logged in</div>;
    }  

    return (
        <div>
            <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
                <Navbar.Brand>
                    <Link className="nav-link" to="/">Camera Search</Link>
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="responsive-navbar-nav" />
                <Navbar.Collapse id="responsive-navbar-nav">
                    <Nav className="mr-auto">
                        <Link className="nav-link" to="/">Home</Link>
                        <NavDropdown title="Admin Tools" id="collasible-nav-dropdown">
                            <LinkContainer to="/registeradmin">
                                <NavDropdown.Item>Register New Admin</NavDropdown.Item>
                            </LinkContainer>
                        </NavDropdown>
                    </Nav>
                    <Nav>                        
                        {
                            (!data || !data.me) ? 
                            (
                                <Link className="nav-link" to="/login">Sign In</Link>
                            ) : 
                            null
                        }

                        {
                            (data && data.me) ? (
                                <Link className="nav-link" to="/bye">Account Settings</Link>
                            ) : null
                        }

                        {
                            (!loading && data && data.me) ? 
                            (
                                <a href="#" className="nav-link" onClick={async() => {
                                    await logout();
                                    setAccessToken('');
                                    await client!.resetStore();
                                }}
                                >
                                    Log Out
                                </a>
                                
                            ) : 
                            null
                        }
                    </Nav>
                </Navbar.Collapse>
            </Navbar>
        </div>
    );
}