import logo_beta from '../assets/logo-beta.png'
import './Header.css'

function Header() {
    return (
        <header className='site-header'>
            <img className='logo' src={logo_beta} alt="Playlytics BETA Logo" />
            <button className='learn-more-btn'>Learn More</button>
        </header>
    )
}

export default Header