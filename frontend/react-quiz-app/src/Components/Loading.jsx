import { useState, useEffect } from 'react';

//one spinner for every page that waits on a fetch.
//it holds off for a moment first-- a local api usually answers faster than that, and a
//spinner that appears and vanishes inside 200ms reads as a flicker rather than progress
export function Loading({ label = 'Loading', delay = 250 }){
    const [show, setShow] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => setShow(true), delay);
        return () => clearTimeout(timer);
    }, [delay]);

    if(!show) return null;

    return(
        <div className="loading" role="status" aria-live="polite">
            <div className="spinner" aria-hidden="true"></div>
            <p className="text-muted">{label}</p>
        </div>
    );
}
