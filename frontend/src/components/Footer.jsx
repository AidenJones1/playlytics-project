import logo_icon from '../assets/logo-icon.png'
import './Footer.css'

function Footer() {
    return (
        <footer className="site-footer">
            <img src={logo_icon} alt="Logo" className="icon" />
            <p className='disclaimer'>
                Playlytics is an independent, unofficial sports analytics platform and is not <br />
                affiliated with, endorsed by, sponsored by, or otherwise associated with the <br />
                National Football League (NFL) or any of its member clubs.  All trademarks <br />
                belong to their respective owners.
            </p>
        </footer>
    )
}

export default Footer;