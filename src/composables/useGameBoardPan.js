import interact from 'interactjs'
import { ref, onMounted, onUnmounted, watch } from 'vue'

export function useGameBoardPan(boardRef, options = {}) {
    const { enabled = true } = options

    const isPanning = ref(false)
    const panOffset = ref({ x: 0, y: 0 })
    const zoom = ref(1)
    let interactable = null

    const updateTransform = () => {
        if (boardRef.value) {
            boardRef.value.style.transform = `translate(${panOffset.value.x}px, ${panOffset.value.y}px) scale(${zoom.value})`
            boardRef.value.style.transformOrigin = '0 0'
        }
    }

    const zoomAtPoint = (delta, clientX, clientY) => {
        if (!boardRef.value) return

        const oldZoom = zoom.value;
        const newZoom = Math.max(0.25, Math.min(3, oldZoom + delta));

        const boardRect = boardRef.value.getBoundingClientRect();

        const mouseX = clientX - boardRect.left;
        const mouseY = clientY - boardRect.top;

        const worldX = (50000 - panOffset.value.x) / oldZoom;
        const worldY = (50000 - panOffset.value.y) / oldZoom;

        zoom.value = newZoom;

        panOffset.value.x = 50000 - worldX * newZoom;
        panOffset.value.y = 50000 - worldY * newZoom;
        
        updateTransform();

    }

    const zoomIn = (step = 0.1, pointX = null, pointY = null) => {
        if (pointX !== null && pointY !== null) {
            zoomAtPoint(step, pointX, pointY)
        } else {
            const centerX = window.innerWidth / 2
            const centerY = window.innerHeight / 2
            zoomAtPoint(step, centerX, centerY)
        }
    }

    const zoomOut = (step = 0.1, pointX = null, pointY = null) => {
        if (pointX !== null && pointY !== null) {
            zoomAtPoint(-step, pointX, pointY)
        } else {
            const centerX = window.innerWidth / 2
            const centerY = window.innerHeight / 2
            zoomAtPoint(-step, centerX, centerY)
        }
    }

    const resetZoom = () => {
        zoom.value = 1
        panOffset.value = { x: 0, y: 0 }
        updateTransform()
    }

    const setZoom = (value) => {
        const oldZoom = zoom.value
        const newZoom = Math.max(0.25, Math.min(3, value))

        const centerX = window.innerWidth / 2
        const centerY = window.innerHeight / 2
        zoomAtPoint(newZoom - oldZoom, centerX, centerY)
    }

    const handleWheel = (event) => {
        if (event.ctrlKey || event.metaKey) {
            event.preventDefault()
            const delta = event.deltaY > 0 ? -0.1 : 0.1
            zoomAtPoint(delta, event.clientX, event.clientY)
        }
    }

    const initPan = () => {
        if (!boardRef.value || !enabled) return

        interactable = interact('.board-pan-area').draggable({
            enabled: true,
            ignoreFrom: '.game-object, .game-object *, button, input, textarea, .draw-canvas, .toolbar',
            listeners: {
                start(event) {
                    const originalEvent = event.originalEvent || event.srcEvent
                    if (originalEvent && !originalEvent.altKey && originalEvent.button !== 1) {
                        return
                    }
                    isPanning.value = true
                    document.body.style.cursor = 'grabbing'
                },
                move(event) {
                    if (!isPanning.value) return
                    panOffset.value.x += event.dx
                    panOffset.value.y += event.dy
                    updateTransform()
                },
                end() {
                    isPanning.value = false
                    document.body.style.cursor = 'default'
                }
            },
            inertia: true,
            modifiers: []
        })
    }

    const handleKeyDown = (event) => {
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return

        const step = event.shiftKey ? 50 : 20

        switch (event.key) {
            case 'ArrowUp': panOffset.value.y += step; updateTransform(); break
            case 'ArrowDown': panOffset.value.y -= step; updateTransform(); break
            case 'ArrowLeft': panOffset.value.x += step; updateTransform(); break
            case 'ArrowRight': panOffset.value.x -= step; updateTransform(); break
            case '0':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault()
                    resetZoom()
                }
                break
            case '+':
            case '=': zoomIn(); break
            case '-':
            case '_': zoomOut(); break
        }
    }

    onMounted(() => {
        initPan()
        window.addEventListener('wheel', handleWheel, { passive: false })
        window.addEventListener('keydown', handleKeyDown)
    })

    onUnmounted(() => {
        window.removeEventListener('wheel', handleWheel)
        window.removeEventListener('keydown', handleKeyDown)
        if (interactable) {
            interactable.unset()
            interactable = null
        }
    })

    watch(enabled, (newValue) => {
        if (interactable) {
            interactable.draggable({ enabled: newValue })
        }
    })

    return {
        isPanning,
        panOffset,
        zoom,
        zoomIn,
        zoomOut,
        resetZoom,
        setZoom
    }
}